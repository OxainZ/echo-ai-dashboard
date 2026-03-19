// Views/Analytics/AnalyticsView.swift
// Echo Copilot — Analytics tab: cumulative P&L curve, R distribution, summary stats

import SwiftUI
import Charts

struct AnalyticsView: View {
    @EnvironmentObject private var env: AppEnvironment
    @State private var vm: AnalyticsViewModel?

    var body: some View {
        NavigationStack {
            Group {
                if let vm {
                    AnalyticsContent(vm: vm)
                } else {
                    ProgressView()
                }
            }
            .navigationTitle("Analytics")
            .navigationBarTitleDisplayMode(.large)
        }
        .onAppear {
            if vm == nil { vm = AnalyticsViewModel(repository: env.journalRepository) }
            vm?.load()
        }
    }
}

// MARK: - Content

private struct AnalyticsContent: View {
    let vm: AnalyticsViewModel

    var body: some View {
        ScrollView {
            VStack(spacing: 20) {
                statsGrid
                if !vm.cumulativePnLPoints.isEmpty { pnlChart }
                if !vm.rDistribution.isEmpty { rChart }
                if vm.bestTrade != nil || vm.worstTrade != nil { highlightCards }
                if vm.closedTrades.isEmpty { emptyState }
            }
            .padding(16)
        }
        .background(Color(.systemGroupedBackground))
    }

    // MARK: - Stats grid

    private var statsGrid: some View {
        LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 12) {
            AnalyticStatCard(
                title: "Total P&L",
                value: vm.closedTrades.isEmpty ? "—" : String(format: "%+.2f", vm.totalPnL),
                valueColor: vm.totalPnL >= 0 ? .green : .red,
                icon: "dollarsign.circle.fill"
            )
            AnalyticStatCard(
                title: "Win Rate",
                value: vm.winRate.map { String(format: "%.0f%%", $0 * 100) } ?? "—",
                valueColor: (vm.winRate ?? 0) >= 0.5 ? .green : .orange,
                icon: "target"
            )
            AnalyticStatCard(
                title: "Avg R",
                value: vm.averageR.map { String(format: "%+.2fR", $0) } ?? "—",
                valueColor: (vm.averageR ?? 0) >= 0 ? .green : .red,
                icon: "arrow.up.right.circle.fill"
            )
            AnalyticStatCard(
                title: "Max Drawdown",
                value: vm.maxDrawdown > 0 ? String(format: "-%.2f", vm.maxDrawdown) : "—",
                valueColor: .red,
                icon: "arrow.down.right.circle.fill"
            )
        }
    }

    // MARK: - Cumulative P&L chart

    private var pnlChart: some View {
        SectionCardView(title: "Cumulative P&L", systemImage: "chart.line.uptrend.xyaxis") {
            let isPositive = vm.totalPnL >= 0
            let lineColor: Color = isPositive ? .green : .red

            Chart(vm.cumulativePnLPoints) { point in
                LineMark(
                    x: .value("Date", point.date),
                    y: .value("P&L", point.cumulativePnL)
                )
                .foregroundStyle(lineColor)
                .interpolationMethod(.catmullRom)

                AreaMark(
                    x: .value("Date", point.date),
                    yStart: .value("Zero", 0),
                    yEnd: .value("P&L", point.cumulativePnL)
                )
                .foregroundStyle(
                    LinearGradient(
                        colors: [lineColor.opacity(0.25), .clear],
                        startPoint: .top,
                        endPoint: .bottom
                    )
                )
                .interpolationMethod(.catmullRom)
            }
            .chartXAxis {
                AxisMarks(values: .automatic(desiredCount: 4)) {
                    AxisGridLine()
                    AxisValueLabel(format: .dateTime.month(.abbreviated).day())
                }
            }
            .chartYAxis {
                AxisMarks { value in
                    AxisGridLine()
                    AxisValueLabel {
                        if let d = value.as(Double.self) {
                            Text(String(format: "%+.0f", d)).font(.caption2)
                        }
                    }
                }
            }
            .frame(height: 190)
            .padding()
        }
    }

    // MARK: - R distribution chart

    private var rChart: some View {
        SectionCardView(title: "R-Multiple Distribution", systemImage: "chart.bar.fill") {
            Chart(vm.rDistribution) { bucket in
                BarMark(
                    x: .value("Range", bucket.label),
                    y: .value("Trades", bucket.count)
                )
                .foregroundStyle(bucket.isWin ? Color.green : Color.red)
                .annotation(position: .top) {
                    Text("\(bucket.count)")
                        .font(.caption2.weight(.semibold))
                        .foregroundStyle(.secondary)
                }
            }
            .chartXAxis {
                AxisMarks { value in
                    AxisValueLabel {
                        if let s = value.as(String.self) {
                            Text(s)
                                .font(.system(size: 9))
                                .rotationEffect(.degrees(-20))
                        }
                    }
                }
            }
            .frame(height: 160)
            .padding()
        }
    }

    // MARK: - Best / worst

    private var highlightCards: some View {
        HStack(spacing: 12) {
            if let best = vm.bestTrade, let pnl = best.pnlDollars {
                TradeHighlightCard(
                    title: "Best Trade",
                    ticker: best.ticker,
                    value: String(format: "+%.2f", pnl),
                    valueColor: .green,
                    icon: "crown.fill"
                )
            }
            if let worst = vm.worstTrade, let pnl = worst.pnlDollars {
                TradeHighlightCard(
                    title: "Worst Trade",
                    ticker: worst.ticker,
                    value: String(format: "%.2f", pnl),
                    valueColor: .red,
                    icon: "exclamationmark.triangle.fill"
                )
            }
        }
    }

    private var emptyState: some View {
        EmptyStateView(
            systemImage: "chart.line.uptrend.xyaxis",
            title: "No Closed Trades",
            subtitle: "Exit a journal trade to start seeing analytics."
        )
        .padding(.top, 60)
    }
}

// MARK: - Subviews

private struct AnalyticStatCard: View {
    let title: String
    let value: String
    let valueColor: Color
    let icon: String

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack(spacing: 4) {
                Image(systemName: icon)
                    .font(.caption)
                    .foregroundStyle(.secondary)
                Text(title)
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
            Text(value)
                .font(.title3.bold().monospacedDigit())
                .foregroundStyle(valueColor)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(14)
        .background(Color(.secondarySystemGroupedBackground), in: RoundedRectangle(cornerRadius: 12))
    }
}

private struct TradeHighlightCard: View {
    let title: String
    let ticker: String
    let value: String
    let valueColor: Color
    let icon: String

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack(spacing: 4) {
                Image(systemName: icon).font(.caption).foregroundStyle(valueColor)
                Text(title).font(.caption).foregroundStyle(.secondary)
            }
            Text(ticker).font(.headline.bold())
            Text(value)
                .font(.subheadline.monospacedDigit())
                .foregroundStyle(valueColor)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(14)
        .background(Color(.secondarySystemGroupedBackground), in: RoundedRectangle(cornerRadius: 12))
    }
}

#Preview {
    AnalyticsView()
        .environmentObject(AppEnvironment.preview)
        .preferredColorScheme(.dark)
}
