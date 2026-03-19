// Views/Orders/OrdersView.swift
// Echo Copilot — Manual order calculator: position sizing

import SwiftUI

struct OrdersView: View {
    @EnvironmentObject private var env: AppEnvironment
    @State private var vm = OrdersViewModel()

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 16) {
                    // Inputs
                    SectionCardView(title: "Setup", systemImage: "pencil.and.outline") {
                        LabeledTextField(label: "Ticker (optional)", text: $vm.selectedTicker,
                                         placeholder: "NVDA", keyboard: .default)
                        LabeledTextField(label: "Entry Price", text: $vm.entryPriceText,
                                         placeholder: "0.00", keyboard: .decimalPad)
                        LabeledTextField(label: "Stop Price", text: $vm.stopPriceText,
                                         placeholder: "0.00", keyboard: .decimalPad)
                        LabeledTextField(label: "Target Price", text: $vm.targetPriceText,
                                         placeholder: "0.00", keyboard: .decimalPad)
                    }

                    // Stop presets
                    SectionCardView(title: "Stop Presets", systemImage: "slider.horizontal.3") {
                        HStack(spacing: 8) {
                            ForEach([0.5, 0.6, 1.0, 2.0], id: \.self) { pct in
                                Button {
                                    vm.applyStopPreset(pct: pct)
                                } label: {
                                    Text("\(pct, specifier: "%.1f")%")
                                        .font(.system(size: 13, weight: .semibold))
                                        .foregroundStyle(.white)
                                        .padding(.horizontal, 12)
                                        .padding(.vertical, 8)
                                        .background(Color(.systemGray4), in: RoundedRectangle(cornerRadius: 8))
                                }
                                .buttonStyle(.plain)
                            }
                        }
                        Text("Applied as stop % below entry price")
                            .font(.caption2)
                            .foregroundStyle(.tertiary)
                    }

                    // Account & risk
                    SectionCardView(title: "Account & Risk", systemImage: "banknote") {
                        LabeledTextField(label: "Account Size ($)", text: $vm.accountSizeText,
                                         placeholder: "50000", keyboard: .decimalPad)
                        LabeledTextField(label: "Risk %", text: $vm.riskPercentText,
                                         placeholder: "1.0", keyboard: .decimalPad)
                    }

                    // Validation error
                    if let err = vm.validationError {
                        HStack {
                            Image(systemName: "exclamationmark.triangle.fill")
                                .foregroundStyle(.orange)
                            Text(err)
                                .font(.caption)
                                .foregroundStyle(.orange)
                        }
                        .padding(.horizontal)
                    }

                    // Computed outputs
                    if let calc = vm.calculation {
                        SectionCardView(title: "Position Sizing", systemImage: "chart.pie.fill") {
                            MetricRowView(label: "Dollar Risk", value: calc.dollarRisk.asCurrency,
                                          highlight: true, valueColor: .orange)
                            MetricRowView(label: "Risk / Share", value: calc.riskPerShare.asPrice)
                            MetricRowView(label: "Max Shares", value: "\(calc.positionSizeShares)",
                                          highlight: true, valueColor: .white)
                            MetricRowView(label: "Position Notional", value: calc.totalPositionCost.asCurrency)
                            Divider()
                            MetricRowView(label: "Reward : Risk", value: String(format: "%.2f : 1", calc.rewardToRisk),
                                          highlight: true, valueColor: calc.rewardToRisk >= 2 ? .green : .yellow)
                            MetricRowView(label: "Projected Profit", value: calc.projectedProfit.asCurrency,
                                          highlight: true, valueColor: .cyan)
                        }

                        // Warnings
                        if let warn = vm.positionWarning {
                            WarningBanner(text: warn, color: .red)
                        }
                        if let warn = vm.rrWarning {
                            WarningBanner(text: warn, color: .orange)
                        }

                        // Copy summary
                        HStack {
                            Spacer()
                            CopyButtonView(
                                text: vm.orderSummaryText,
                                label: "Copy Order Summary",
                                icon: "doc.on.doc"
                            )
                            Spacer()
                        }
                    } else {
                        SectionCardView(title: "Position Sizing", systemImage: "chart.pie.fill") {
                            Text("Fill in entry, stop, target, account, and risk % to compute sizing.")
                                .font(.subheadline)
                                .foregroundStyle(.secondary)
                        }
                    }
                }
                .padding(16)
            }
            .navigationTitle("Order Helper")
            .navigationBarTitleDisplayMode(.large)
        }
    }
}

// MARK: - Warning banner

private struct WarningBanner: View {
    let text: String
    let color: Color

    var body: some View {
        HStack(alignment: .top, spacing: 8) {
            Image(systemName: "exclamationmark.triangle.fill")
                .foregroundStyle(color)
                .font(.caption)
            Text(text)
                .font(.caption)
                .foregroundStyle(color)
                .fixedSize(horizontal: false, vertical: true)
        }
        .padding(10)
        .background(color.opacity(0.1), in: RoundedRectangle(cornerRadius: 8))
    }
}

// MARK: - Labeled text field

private struct LabeledTextField: View {
    let label: String
    @Binding var text: String
    let placeholder: String
    var keyboard: UIKeyboardType = .default

    var body: some View {
        HStack {
            Text(label)
                .font(.subheadline)
                .foregroundStyle(.secondary)
                .frame(minWidth: 130, alignment: .leading)
            TextField(placeholder, text: $text)
                .keyboardType(keyboard)
                .multilineTextAlignment(.trailing)
                .font(.subheadline.monospacedDigit())
        }
    }
}

#Preview {
    OrdersView()
        .environmentObject(AppEnvironment.preview)
        .preferredColorScheme(.dark)
}
