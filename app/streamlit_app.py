"""DataLens AI — Streamlit Dashboard."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import streamlit as st

st.set_page_config(
    page_title="DataLens AI",
    page_icon="\U0001f52c",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject custom CSS
css_path = Path(__file__).parent / "styles" / "custom.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)

from datalens_ai import __version__  # noqa: E402
from datalens_ai.core.config import get_available_providers, is_demo_mode  # noqa: E402


def main():
    """Main app entry point."""
    _sidebar()

    # Hero header
    st.markdown(
        '<h1 style="text-align:center;">'
        '<span class="hero-gradient">DataLens AI</span>'
        '</h1>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p style="text-align:center;color:#94A3B8;font-size:1.1rem;">'
        "Upload data. Ask questions. Get insights."
        "</p>",
        unsafe_allow_html=True,
    )

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "\U0001f4c2 Data Explorer",
        "\U0001f4ac Ask Questions",
        "\U0001f4a1 AI Insights",
        "\U0001f4d6 Data Stories",
        "\U0001f50d Schema Explorer",
    ])

    with tab1:
        _data_explorer_tab()
    with tab2:
        _query_tab()
    with tab3:
        _insights_tab()
    with tab4:
        _stories_tab()
    with tab5:
        _schema_tab()


def _sidebar():
    with st.sidebar:
        st.markdown(
            '<h2 style="text-align:center;">'
            '\U0001f52c DataLens AI</h2>',
            unsafe_allow_html=True,
        )
        st.caption(f"v{__version__}")

        if is_demo_mode():
            st.info(
                "\U0001f3af **Demo Mode** — No API keys needed! "
                "Using rule-based analysis."
            )
        else:
            st.success("\U0001f511 Gemini API key detected")

        st.divider()
        st.subheader("Providers")
        for p in get_available_providers():
            icon = "\u2705" if p["available"] else "\u274c"
            st.text(f"{icon} {p['name']} ({p['cost']})")

        st.divider()
        st.caption("Built by [Mekala Ajay](https://linkedin.com/in/ajaymekala)")
        st.caption("[GitHub](https://github.com/mekala27-45/datalens-ai)")


def _get_engine():
    """Get or create the DuckDB engine in session state."""
    if "engine" not in st.session_state:
        from datalens_ai.engine.duckdb_engine import DuckDBEngine
        st.session_state["engine"] = DuckDBEngine()
    return st.session_state["engine"]


def _data_explorer_tab():
    """Tab 1: Upload data and auto-profile it."""
    from datalens_ai.ingestion.loader import load_file, load_from_bytes
    from datalens_ai.ingestion.profiler import profile_table
    from datalens_ai.ingestion.quality import score_quality
    from datalens_ai.ingestion.samples import list_sample_datasets, get_sample_file_paths

    st.header("\U0001f4c2 Data Explorer")
    st.markdown("Upload your data or try a sample dataset to get started.")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Upload File")
        uploaded = st.file_uploader(
            "Drag and drop a file",
            type=["csv", "tsv", "xlsx", "xls", "json", "parquet"],
            key="file_upload",
        )
        if uploaded:
            engine = _get_engine()
            table_name = load_from_bytes(
                engine.connection, uploaded.read(), uploaded.name
            )
            engine._update_schema_cache(table_name)
            st.session_state["table_name"] = table_name
            st.success(f"Loaded **{uploaded.name}** as `{table_name}`")

    with col2:
        st.subheader("Sample Datasets")
        samples = list_sample_datasets()
        if samples:
            cols = st.columns(2)
            for i, (key, info) in enumerate(samples.items()):
                with cols[i % 2]:
                    if st.button(
                        f"{info.icon} {info.display_name}",
                        key=f"sample_{key}",
                        use_container_width=True,
                    ):
                        engine = _get_engine()
                        paths = get_sample_file_paths(key)
                        for p in paths:
                            table_name = load_file(engine.connection, p)
                            engine._update_schema_cache(table_name)
                        st.session_state["table_name"] = table_name
                        st.session_state["sample_key"] = key
                        st.success(
                            f"Loaded **{info.display_name}** "
                            f"({info.row_count:,} rows)"
                        )

    # Profile the loaded data
    table_name = st.session_state.get("table_name")
    if table_name:
        st.divider()
        engine = _get_engine()

        if f"profile_{table_name}" not in st.session_state:
            with st.spinner("Profiling your data..."):
                profile = profile_table(engine.connection, table_name)
                quality, issues = score_quality(profile)
                profile.quality_score = quality
                profile.quality_issues = issues
                st.session_state[f"profile_{table_name}"] = profile

        profile = st.session_state[f"profile_{table_name}"]

        # KPI row
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Rows", f"{profile.row_count:,}")
        k2.metric("Columns", profile.column_count)
        k3.metric("Quality Score", f"{profile.quality_score:.0f}/100")
        k4.metric("Issues", len(profile.quality_issues))

        # Column details
        st.subheader("Column Profiles")
        for col in profile.columns:
            with st.expander(
                f"**{col.name}** — {col.dtype}"
                f" ({col.semantic_type or 'general'})"
            ):
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Nulls", f"{col.null_pct:.1%}")
                c2.metric("Unique", f"{col.unique_count:,}")
                c3.metric("Cardinality", col.cardinality)
                c4.metric("Type", col.dtype)

                if col.sample_values:
                    st.caption(
                        f"Samples: {', '.join(col.sample_values[:5])}"
                    )

        # Suggested questions
        if profile.suggested_questions:
            st.subheader("\U0001f4a1 Suggested Questions")
            for q in profile.suggested_questions[:6]:
                st.markdown(f"- {q}")


def _query_tab():
    """Tab 2: Natural language query interface."""
    from datalens_ai.ai.nl_to_sql import NLToSQLOrchestrator
    from datalens_ai.ai.insight_generator import generate_insights
    from datalens_ai.engine.result_analyzer import ResultAnalyzer
    from datalens_ai.visualization.chart_selector import recommend_chart
    from datalens_ai.visualization.chart_factory import create_chart
    import pandas as pd

    st.header("\U0001f4ac Ask Questions")

    table_name = st.session_state.get("table_name")
    if not table_name:
        st.info("Load a dataset first in the Data Explorer tab.")
        return

    engine = _get_engine()

    # Show suggested questions as clickable chips
    profile_key = f"profile_{table_name}"
    if profile_key in st.session_state:
        profile = st.session_state[profile_key]
        if profile.suggested_questions:
            st.markdown("**Try a question:**")
            chip_cols = st.columns(min(4, len(profile.suggested_questions)))
            for i, q in enumerate(profile.suggested_questions[:4]):
                with chip_cols[i]:
                    if st.button(
                        q[:40] + "..." if len(q) > 40 else q,
                        key=f"chip_{i}",
                        use_container_width=True,
                    ):
                        st.session_state["current_question"] = q

    # Chat input
    question = st.chat_input(
        "Ask anything about your data...",
        key="query_input",
    )
    if not question:
        question = st.session_state.pop("current_question", None)
    if not question:
        st.info(
            "Type a question like *'What are the top 5 products by revenue?'*"
        )
        return

    # Process query
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):
            if "orchestrator" not in st.session_state:
                st.session_state["orchestrator"] = NLToSQLOrchestrator(engine)
            orch = st.session_state["orchestrator"]
            result = orch.process(question, table_name)

        if result.error:
            st.error(f"Error: {result.error}")
            return

        # Show SQL
        with st.expander("\U0001f4dd SQL Query", expanded=False):
            st.code(result.sql_query, language="sql")
            if result.sql_explanation:
                st.caption(result.sql_explanation)

        st.caption(
            f"{result.row_count} rows \u2022 "
            f"{result.execution_time_ms:.1f}ms"
        )

        # Auto-visualize
        if result.data:
            df = pd.DataFrame(result.data)
            analyzer = ResultAnalyzer()
            shape = analyzer.analyze(df)

            chart_hint = None
            if result.chart_recommendation:
                chart_hint = result.chart_recommendation.chart_type

            rec = recommend_chart(shape, chart_hint)
            result.chart_recommendation = rec

            if rec.chart_type != "table":
                fig = create_chart(df, rec, title="")
                st.plotly_chart(
                    fig, use_container_width=True,
                    key=f"chart_{result.id}",
                )

                # Alternative chart types
                alt_cols = st.columns(len(rec.alternatives[:3]) + 1)
                with alt_cols[0]:
                    st.caption(f"Showing: **{rec.chart_type}**")
                for j, alt in enumerate(rec.alternatives[:3]):
                    with alt_cols[j + 1]:
                        if st.button(
                            f"Switch to {alt}",
                            key=f"alt_{result.id}_{alt}",
                        ):
                            alt_rec = rec.model_copy()
                            alt_rec.chart_type = alt
                            fig2 = create_chart(df, alt_rec)
                            st.plotly_chart(
                                fig2, use_container_width=True,
                                key=f"alt_chart_{result.id}_{alt}",
                            )

            # Data table
            with st.expander("View data table", expanded=False):
                st.dataframe(
                    df, use_container_width=True, hide_index=True,
                    key=f"df_{result.id}",
                )

            # Insights
            insights = generate_insights(df, question)
            if insights:
                st.subheader("\U0001f4a1 Insights")
                for insight in insights:
                    st.markdown(f"- {insight}")

    # Save to history
    if "query_history" not in st.session_state:
        st.session_state["query_history"] = []
    st.session_state["query_history"].append(result)


def _insights_tab():
    """Tab 3: Automatic AI insights."""
    st.header("\U0001f4a1 AI Insights")

    table_name = st.session_state.get("table_name")
    if not table_name:
        st.info("Load a dataset first in the Data Explorer tab.")
        return

    profile_key = f"profile_{table_name}"
    if profile_key not in st.session_state:
        st.info("Profile your data first in the Data Explorer tab.")
        return

    profile = st.session_state[profile_key]

    # Quality insights
    st.subheader("\U0001f3af Data Quality")
    score = profile.quality_score
    color = (
        "#10B981" if score >= 80
        else "#F59E0B" if score >= 60
        else "#EF4444"
    )
    st.markdown(
        f'<div style="text-align:center;padding:20px;">'
        f'<span style="font-size:3rem;font-weight:700;color:{color};">'
        f"{score:.0f}</span>"
        f'<span style="font-size:1.5rem;color:#94A3B8;">/100</span>'
        f"</div>",
        unsafe_allow_html=True,
    )

    if profile.quality_issues:
        for issue in profile.quality_issues:
            icon = {
                "critical": "\U0001f534",
                "warning": "\U0001f7e1",
                "info": "\U0001f535",
            }.get(issue.severity, "\u2139\ufe0f")
            st.markdown(
                f"{icon} **{issue.issue_type}** "
                f"({issue.column or 'general'}): {issue.description}"
            )
    else:
        st.success("No quality issues found!")

    # Correlations
    if profile.correlations:
        st.subheader("\U0001f517 Correlations")
        for corr in profile.correlations[:5]:
            emoji = "\U0001f7e2" if corr.strength == "strong" else "\U0001f7e1"
            st.markdown(
                f"{emoji} **{corr.column_a}** \u2194 **{corr.column_b}**: "
                f"{corr.correlation:.3f} ({corr.strength})"
            )

    # Column distribution charts
    st.subheader("\U0001f4ca Column Distributions")
    numeric_cols = [c for c in profile.columns if c.dtype == "numeric"]
    if numeric_cols:
        import plotly.express as px
        engine = _get_engine()
        df = engine.connection.execute(
            f'SELECT * FROM "{table_name}"'
        ).fetchdf()

        cols = st.columns(min(3, len(numeric_cols)))
        for i, col in enumerate(numeric_cols[:6]):
            with cols[i % 3]:
                fig = px.histogram(
                    df, x=col.name, nbins=20,
                    title=col.name,
                    color_discrete_sequence=["#6366F1"],
                )
                fig.update_layout(
                    height=250, margin=dict(l=20, r=20, t=40, b=20),
                    showlegend=False,
                )
                st.plotly_chart(
                    fig, use_container_width=True,
                    key=f"dist_{col.name}",
                )


def _stories_tab():
    """Tab 4: Data story builder."""
    st.header("\U0001f4d6 Data Stories")

    history = st.session_state.get("query_history", [])
    if not history:
        st.info(
            "Ask some questions first in the Ask Questions tab. "
            "Your queries will appear here as story building blocks."
        )
        return

    st.subheader("Your Query History")
    for i, result in enumerate(history):
        if result.success:
            with st.expander(
                f"\U0001f4dd {result.question} ({result.row_count} rows)"
            ):
                st.code(result.sql_query, language="sql")
                if result.insights:
                    for ins in result.insights:
                        st.markdown(f"- {ins}")

    # Export
    st.divider()
    st.subheader("Export")

    import json
    export_data = []
    for r in history:
        if r.success:
            export_data.append({
                "question": r.question,
                "sql": r.sql_query,
                "row_count": r.row_count,
                "execution_time_ms": r.execution_time_ms,
                "insights": r.insights,
            })

    json_str = json.dumps(export_data, indent=2)
    st.download_button(
        "\U0001f4e5 Download Query History (JSON)",
        json_str,
        "datalens_queries.json",
        mime="application/json",
        key="dl_history",
    )


def _schema_tab():
    """Tab 5: Schema explorer."""
    st.header("\U0001f50d Schema Explorer")

    table_name = st.session_state.get("table_name")
    if not table_name:
        st.info("Load a dataset first in the Data Explorer tab.")
        return

    engine = _get_engine()
    schema = engine.get_schema(table_name)

    st.subheader(f"Table: `{table_name}`")
    st.write(f"**Rows:** {engine.get_row_count(table_name):,}")

    if schema:
        import pandas as pd
        schema_df = pd.DataFrame(schema)
        st.dataframe(
            schema_df, use_container_width=True, hide_index=True,
            key="schema_df",
        )

    # Sample data
    st.subheader("Sample Data")
    samples = engine.get_sample_rows(table_name, 10)
    if samples:
        import pandas as pd
        st.dataframe(
            pd.DataFrame(samples),
            use_container_width=True, hide_index=True,
            key="sample_df",
        )

    # Full SQL console
    st.subheader("\U0001f4bb SQL Console")
    user_sql = st.text_area(
        "Write custom SQL",
        value=f'SELECT * FROM "{table_name}" LIMIT 10',
        height=100,
        key="sql_console",
    )
    if st.button("Run SQL", type="primary", key="run_sql"):
        try:
            df, ms = engine.execute_sql(user_sql, limit=1000)
            st.caption(f"{len(df)} rows in {ms:.1f}ms")
            st.dataframe(
                df, use_container_width=True, hide_index=True,
                key="sql_result",
            )
        except Exception as e:
            st.error(f"Error: {e}")


if __name__ == "__main__":
    main()
