// Views/Journal/CloseTradeView.swift
// Echo Copilot — Focused sheet for exiting an open trade position

import SwiftUI

struct CloseTradeView: View {
    let entry: JournalEntry
    let onClose: (Double, Date) -> Void

    @Environment(\.dismiss) private var dismiss
    @State private var exitPriceText: String = ""
    @State private var exitDate: Date = Date()

    var body: some View {
        NavigationStack {
            Form {
                // Summary header
                Section {
                    HStack {
                        VStack(alignment: .leading, spacing: 4) {
                            Text(entry.ticker.uppercased())
                                .font(.headline.bold())
                            Text("Entry: \(entry.entryPrice.asPrice)")
                                .font(.subheadline)
                                .foregroundStyle(.secondary)
                        }
                        Spacer()
                        if let stop = entry.stopPrice {
                            VStack(alignment: .trailing, spacing: 4) {
                                Text("Stop: \(stop.asPrice)")
                                    .font(.caption)
                                    .foregroundStyle(.red)
                                if let risk = entry.pnlR, let exit = Double(exitPriceText) {
                                    let _ = exit  // suppress unused warning
                                    Text("Risk/share: \(abs(entry.entryPrice - stop).asPrice)")
                                        .font(.caption2)
                                        .foregroundStyle(.secondary)
                                }
                            }
                        }
                    }
                }

                // Exit fields
                Section("Exit") {
                    HStack {
                        Text("Exit Price")
                        Spacer()
                        TextField("0.00", text: $exitPriceText)
                            .keyboardType(.decimalPad)
                            .multilineTextAlignment(.trailing)
                            .font(.body.monospacedDigit())
                    }
                    DatePicker("Exit Date", selection: $exitDate, displayedComponents: .date)
                }

                // Live P&L preview
                if let exitPrice = Double(exitPriceText), exitPrice > 0 {
                    let pnl = exitPrice - entry.entryPrice
                    Section("P&L Preview") {
                        HStack {
                            Text("Dollar P&L")
                            Spacer()
                            Text(String(format: pnl >= 0 ? "+%.2f" : "%.2f", pnl))
                                .font(.body.bold().monospacedDigit())
                                .foregroundStyle(pnl >= 0 ? .green : .red)
                        }

                        if let stop = entry.stopPrice {
                            let riskPerShare = abs(entry.entryPrice - stop)
                            if riskPerShare > 0 {
                                let rMultiple = pnl / riskPerShare
                                HStack {
                                    Text("R-Multiple")
                                    Spacer()
                                    Text(String(format: rMultiple >= 0 ? "+%.2fR" : "%.2fR", rMultiple))
                                        .font(.body.bold().monospacedDigit())
                                        .foregroundStyle(rMultiple >= 0 ? .green : .orange)
                                }
                            }
                        }
                    }
                }
            }
            .navigationTitle("Close Trade")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    Button("Cancel") { dismiss() }
                }
                ToolbarItem(placement: .topBarTrailing) {
                    Button("Close Trade") {
                        if let price = Double(exitPriceText), price > 0 {
                            onClose(price, exitDate)
                            dismiss()
                        }
                    }
                    .fontWeight(.semibold)
                    .disabled(Double(exitPriceText) == nil || (Double(exitPriceText) ?? 0) <= 0)
                }
            }
        }
    }
}

#Preview {
    CloseTradeView(entry: JournalEntry.previewEntry) { _, _ in }
        .preferredColorScheme(.dark)
}
