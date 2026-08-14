"""Tests unitarios para el CLI (main.py), con red y gráficos simulados."""

import logging

import pytest

import main


@pytest.fixture
def cli_args(monkeypatch):
    """Parsea argumentos del CLI como si vinieran de la línea de comandos."""

    def _parse(*argv):
        monkeypatch.setattr(main.sys, "argv", ["main.py", *argv])
        return main.parse_args()

    return _parse


@pytest.fixture
def analyzer_calls(monkeypatch, offline_report):
    """Reemplaza ForexVolatilityAnalyzer por un doble que no usa la red."""

    recorded: list[dict] = []

    class StubAnalyzer:
        def analyze(self, **kwargs):
            recorded.append(kwargs)
            return offline_report

    monkeypatch.setattr(main, "ForexVolatilityAnalyzer", StubAnalyzer)
    return recorded


@pytest.fixture
def stub_plots(monkeypatch):
    """Captura las llamadas a las funciones de graficado."""
    calls = {"png": [], "html": [], "comparison": []}
    monkeypatch.setattr(
        main,
        "plot_full_analysis",
        lambda report, save_path=None, show=True: calls["png"].append((save_path, show)),
    )
    monkeypatch.setattr(
        main,
        "plot_interactive_analysis",
        lambda report, save_path=None, show=True: calls["html"].append((save_path, show)),
    )
    monkeypatch.setattr(
        main,
        "plot_comparison",
        lambda df, save_path=None, show=True: calls["comparison"].append(
            (save_path, show)
        ),
    )
    return calls


class TestParseArgs:
    def test_defaults(self, cli_args):
        args = cli_args()

        assert args.pair is None
        assert args.period == "3m"
        assert args.window == 20
        assert args.format == "png"
        assert not any(
            [args.compare, args.save, args.no_plot, args.list, args.verbose,
             args.indicators, args.predict]
        )

    def test_parses_flags_and_values(self, cli_args):
        args = cli_args(
            "--pair", "usdcop", "--period", "6m", "--window", "10",
            "--format", "both", "--indicators", "--predict", "--save", "--verbose",
        )

        assert (args.pair, args.period, args.window, args.format) == (
            "usdcop", "6m", 10, "both",
        )
        assert args.indicators and args.predict and args.save and args.verbose

    def test_parses_multiple_pairs(self, cli_args):
        args = cli_args("--compare", "--pairs", "EURUSD", "GBPUSD")

        assert args.compare is True
        assert args.pairs == ["EURUSD", "GBPUSD"]

    @pytest.mark.parametrize(
        "argv", [("--period", "5d"), ("--format", "svg")]
    )
    def test_rejects_invalid_choices(self, cli_args, argv):
        with pytest.raises(SystemExit):
            cli_args(*argv)


class TestSetupLogging:
    @pytest.mark.parametrize(
        "verbose,expected", [(False, logging.INFO), (True, logging.DEBUG)]
    )
    def test_sets_root_level(self, verbose, expected):
        main.setup_logging(verbose)

        assert logging.getLogger().level == expected


class TestListPairs:
    def test_prints_every_supported_pair(self, capsys):
        main.list_pairs()
        out = capsys.readouterr().out

        for ticker in main.FOREX_PAIRS:
            assert ticker in out


class TestGetSavePath:
    @pytest.mark.parametrize(
        "fmt,expected",
        [
            ("png", "data/EURUSD_3m_analysis.png"),
            ("html", "data/EURUSD_3m_interactive.html"),
            ("both", "data/EURUSD_3m_interactive.html"),
        ],
    )
    def test_path_depends_on_format(self, fmt, expected):
        assert main.get_save_path("eur/usd", "3m", fmt) == expected

    def test_rejects_invalid_pair(self):
        with pytest.raises(ValueError, match="no válido"):
            main.get_save_path("../../etc/passwd", "3m", "png")


class TestRunSingleAnalysis:
    def test_forwards_cli_options_to_analyzer(self, cli_args, analyzer_calls, stub_plots):
        main.run_single_analysis(
            cli_args("--pair", "eur/usd", "--period", "6m", "--window", "10", "--indicators")
        )

        assert analyzer_calls == [
            {
                "pair": "EURUSD",
                "period": "6m",
                "window": 10,
                "start_date": None,
                "end_date": None,
                "include_indicators": True,
            }
        ]

    def test_prints_report_summary(self, cli_args, analyzer_calls, stub_plots, capsys):
        main.run_single_analysis(cli_args("--pair", "EURUSD", "--no-plot"))

        assert "ANÁLISIS DE VOLATILIDAD" in capsys.readouterr().out

    @pytest.mark.parametrize(
        "fmt,expected",
        [("png", {"png": 1, "html": 0}), ("html", {"png": 0, "html": 1}), ("both", {"png": 1, "html": 1})],
    )
    def test_format_selects_plot_backends(self, cli_args, analyzer_calls, stub_plots, fmt, expected):
        main.run_single_analysis(cli_args("--pair", "EURUSD", "--format", fmt))

        assert len(stub_plots["png"]) == expected["png"]
        assert len(stub_plots["html"]) == expected["html"]

    def test_no_plot_skips_all_plotting(self, cli_args, analyzer_calls, stub_plots):
        main.run_single_analysis(cli_args("--pair", "EURUSD", "--format", "both", "--no-plot"))

        assert stub_plots["png"] == [] and stub_plots["html"] == []

    def test_save_passes_paths_and_disables_show(self, cli_args, analyzer_calls, stub_plots):
        main.run_single_analysis(cli_args("--pair", "EURUSD", "--format", "both", "--save"))

        assert stub_plots["png"] == [("data/EURUSD_3m_analysis.png", False)]
        assert stub_plots["html"] == [("data/EURUSD_3m_interactive.html", False)]

    def test_without_save_shows_plot_and_omits_path(self, cli_args, analyzer_calls, stub_plots):
        main.run_single_analysis(cli_args("--pair", "EURUSD"))

        assert stub_plots["png"] == [(None, True)]

    def test_predict_prints_projection_block(self, cli_args, analyzer_calls, stub_plots, capsys):
        main.run_single_analysis(cli_args("--pair", "EURUSD", "--predict", "--no-plot"))
        out = capsys.readouterr().out

        assert "PROYECCIONES BÁSICAS" in out
        for label in ["Tendencia", "Precio Proyectado", "Rango Esperado (ATR)", "Variación Esperada"]:
            assert label in out

    def test_omits_projection_block_by_default(self, cli_args, analyzer_calls, stub_plots, capsys):
        main.run_single_analysis(cli_args("--pair", "EURUSD", "--no-plot"))

        assert "PROYECCIONES" not in capsys.readouterr().out

    def test_invalid_pair_raises(self, cli_args, analyzer_calls, stub_plots):
        with pytest.raises(ValueError, match="no válido"):
            main.run_single_analysis(cli_args("--pair", "EUR"))

    def test_prompts_when_pair_missing(self, cli_args, analyzer_calls, stub_plots, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda *a: "gbp/usd")
        main.run_single_analysis(cli_args("--no-plot"))

        assert analyzer_calls[0]["pair"] == "GBPUSD"


class TestPromptPair:
    def test_reprompts_until_pair_is_valid(self, monkeypatch, capsys):
        answers = iter(["", "EUR", " eurusd "])
        monkeypatch.setattr("builtins.input", lambda *a: next(answers))

        assert main._prompt_pair() == "EURUSD"
        assert capsys.readouterr().out.count("no válido") == 2


class TestRunComparison:
    def test_defaults_to_all_known_pairs(self, cli_args, stub_plots, comparison_df, monkeypatch):
        recorded = {}

        class StubAnalyzer:
            def compare_pairs(self, pairs, period="3m", window=20):
                recorded["pairs"] = pairs
                return comparison_df

        monkeypatch.setattr(main, "ForexVolatilityAnalyzer", StubAnalyzer)
        main.run_comparison(cli_args("--compare", "--no-plot"))

        assert recorded["pairs"] == list(main.FOREX_PAIRS)
        assert stub_plots["comparison"] == []

    def test_uses_explicit_pairs_and_prints_table(self, cli_args, stub_plots, comparison_df, monkeypatch, capsys):
        recorded = {}

        class StubAnalyzer:
            def compare_pairs(self, pairs, period="3m", window=20):
                recorded.update(pairs=pairs, period=period, window=window)
                return comparison_df

        monkeypatch.setattr(main, "ForexVolatilityAnalyzer", StubAnalyzer)
        main.run_comparison(cli_args("--compare", "--pairs", "EURUSD", "GBPUSD", "--period", "6m", "--window", "5", "--no-plot"))

        assert recorded == {"pairs": ["EURUSD", "GBPUSD"], "period": "6m", "window": 5}
        assert "volatility_annual_pct" in capsys.readouterr().out

    def test_save_writes_comparison_path(self, cli_args, stub_plots, comparison_df, monkeypatch):
        class StubAnalyzer:
            def compare_pairs(self, pairs, period="3m", window=20):
                return comparison_df

        monkeypatch.setattr(main, "ForexVolatilityAnalyzer", StubAnalyzer)
        main.run_comparison(cli_args("--compare", "--period", "6m", "--save"))

        assert stub_plots["comparison"] == [("data/comparison_6m.png", False)]


class TestMain:
    def test_list_short_circuits(self, monkeypatch, capsys):
        monkeypatch.setattr(main.sys, "argv", ["main.py", "--list", "--pair", "EURUSD"])
        called = []
        monkeypatch.setattr(main, "run_single_analysis", lambda args: called.append(1))
        main.main()

        assert called == []
        assert "EURUSD" in capsys.readouterr().out

    def test_dispatches_to_single_analysis(self, monkeypatch):
        monkeypatch.setattr(main.sys, "argv", ["main.py", "--pair", "EURUSD"])
        calls = []
        monkeypatch.setattr(main, "run_single_analysis", lambda args: calls.append(args.pair))
        main.main()

        assert calls == ["EURUSD"]

    def test_dispatches_to_comparison(self, monkeypatch):
        monkeypatch.setattr(main.sys, "argv", ["main.py", "--compare"])
        calls = []
        monkeypatch.setattr(main, "run_comparison", lambda args: calls.append(args.compare))
        main.main()

        assert calls == [True]

    def test_value_error_exits_with_message(self, monkeypatch):
        monkeypatch.setattr(main.sys, "argv", ["main.py", "--pair", "EURUSD"])

        def boom(args):
            raise ValueError("sin datos")

        monkeypatch.setattr(main, "run_single_analysis", boom)
        with pytest.raises(SystemExit) as exc:
            main.main()

        assert "sin datos" in str(exc.value)
