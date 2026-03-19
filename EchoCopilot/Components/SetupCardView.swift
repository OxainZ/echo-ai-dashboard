// Components/SetupCardView.swift
// Echo Copilot — Compact radar list card for a TickerSetup

import SwiftUI

struct SetupCardView: View {
    let setup: TickerSetup

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            // Header row
            HStack(alignment: .top) {
                VStack(alignment: .leading, spacing: 3) {
                    Text(setup.symbol)
                        .font(.title3.bold())
                    if let name = setup.companyName {
                        Text(name)
                            .font(.caption)
                            .foregroundStyle(.secondary)
                            .lineLimit(1)
                    }
                }

                Spacer()

                VStack(alignment: .trailing, spacing: 4) {
                    HStack(spacing: 4) {
                        StatusBadgeView(status: setup.status)
                        LaneBadgeView(lane: setup.lane)
                    }
                    ComplianceBadgeView(compliance: setup.cashCompliance)
                }
            }

            Divider()

            // Key levels
            HStack(spacing: 0) {
                LevelCell(label: "Price", value: setup.price?.asPrice ?? "—")
                LevelCell(label: "PMH", value: setup.pmh.asPrice)
                LevelCell(label: "PDH", value: setup.pdh.asPrice)
                LevelCell(label: "Trigger", value: setup.trigger?.asPrice ?? "—", accent: .green)
            }

            // Metrics
            HStack(spacing: 0) {
                LevelCell(label: "RVOL", value: setup.rvol?.asMultiplier ?? "—", accent: rvolColor)
                LevelCell(label: "Vol-Z", value: setup.volZ?.rounded2 ?? "—")
                LevelCell(label: "Spread", value: setup.spreadPct?.asPercent ?? "—", accent: spreadColor)
                LevelCell(label: "T1", value: setup.target1?.asPrice ?? "—", accent: .cyan)
            }

            // Shadow warning
            if setup.status == .shadow && !setup.shadowReasons.isEmpty {
                HStack(spacing: 4) {
                    Image(systemName: "exclamationmark.triangle.fill")
                        .font(.caption2)
                        .foregroundStyle(.orange)
                    Text(setup.shadowReasons.prefix(2).map { $0.description }.joined(separator: " · "))
                        .font(.caption2)
                        .foregroundStyle(.orange)
                        .lineLimit(1)
                }
            }

            // Timestamp
            HStack {
                Spacer()
                Text(setup.timestamp.asTimeString)
                    .font(.caption2)
                    .foregroundStyle(.tertiary)
            }
        }
        .padding(14)
        .background(Color(.systemGray6), in: RoundedRectangle(cornerRadius: 14))
    }

    // MARK: - Derived colors

    private var rvolColor: Color {
        guard let rvol = setup.rvol else { return .secondary }
        return rvol >= 2.0 ? .green : rvol >= 1.5 ? .yellow : .orange
    }

    private var spreadColor: Color {
        let threshold = setup.lane == .main ? 0.35 : 0.25
        guard let spread = setup.spreadPct else { return .secondary }
        return spread <= threshold ? .green : .red
    }
}

// MARK: - Sub-component

private struct LevelCell: View {
    let label: String
    let value: String
    var accent: Color = .primary

    var body: some View {
        VStack(spacing: 2) {
            Text(label)
                .font(.system(size: 9))
                .foregroundStyle(.tertiary)
            Text(value)
                .font(.system(size: 12, weight: .semibold, design: .monospaced))
                .foregroundStyle(accent)
        }
        .frame(maxWidth: .infinity)
    }
}

#Preview {
    SetupCardView(setup: TickerSetup.previewActionable)
        .padding()
        .background(.black)
}
