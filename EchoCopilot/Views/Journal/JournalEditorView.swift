// Views/Journal/JournalEditorView.swift
// Echo Copilot — Add / edit journal entry form

import SwiftUI

struct JournalEditorView: View {
    var editingEntry: JournalEntry? = nil
    var prefillTicker: String? = nil

    @EnvironmentObject private var env: AppEnvironment
    @Environment(\.dismiss) private var dismiss
    @State private var vm: JournalEditorViewModel?

    var body: some View {
        NavigationStack {
            Group {
                if let vm = vm {
                    EditorForm(vm: vm, dismiss: dismiss)
                } else {
                    ProgressView()
                }
            }
            .navigationTitle(editingEntry != nil ? "Edit Trade" : "New Trade")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    Button("Cancel") { dismiss() }
                }
                ToolbarItem(placement: .topBarTrailing) {
                    Button("Save") {
                        if let vm = vm, vm.canSave {
                            try? vm.save()
                            dismiss()
                        }
                    }
                    .disabled(vm?.canSave != true)
                    .fontWeight(.semibold)
                }
            }
        }
        .onAppear {
            let newVM = JournalEditorViewModel(repository: env.journalRepository)
            if let existing = editingEntry {
                newVM.load(entry: existing)
            } else if let ticker = prefillTicker {
                newVM.ticker = ticker
            }
            vm = newVM
        }
    }
}

// MARK: - Editor form

private struct EditorForm: View {
    @Bindable var vm: JournalEditorViewModel
    let dismiss: DismissAction

    var body: some View {
        Form {
            // Basic info
            Section("Trade") {
                HStack {
                    Text("Ticker")
                    Spacer()
                    TextField("NVDA", text: $vm.ticker)
                        .multilineTextAlignment(.trailing)
                        .textCase(.uppercase)
                }

                DatePicker("Entry Date", selection: $vm.entryDate)

                Toggle("Has Exit Date", isOn: $vm.hasExitDate)
                if vm.hasExitDate {
                    DatePicker("Exit Date", selection: $vm.exitDate)
                }
            }

            // Prices
            Section("Prices") {
                PriceRow(label: "Entry Price *", text: $vm.entryPriceText, placeholder: "0.00")

                Toggle("Has Exit Price", isOn: $vm.hasExitPrice)
                if vm.hasExitPrice {
                    PriceRow(label: "Exit Price", text: $vm.exitPriceText, placeholder: "0.00")
                }

                Toggle("Has Stop Price", isOn: $vm.hasStopPrice)
                if vm.hasStopPrice {
                    PriceRow(label: "Stop Price", text: $vm.stopPriceText, placeholder: "0.00")
                }

                Toggle("Has Target 1", isOn: $vm.hasTarget1)
                if vm.hasTarget1 {
                    PriceRow(label: "Target 1", text: $vm.target1Text, placeholder: "0.00")
                }

                Toggle("Has Target 2", isOn: $vm.hasTarget2)
                if vm.hasTarget2 {
                    PriceRow(label: "Target 2", text: $vm.target2Text, placeholder: "0.00")
                }
            }

            // Computed PnL preview
            if let pnl = vm.computedPnL {
                Section("Computed P&L") {
                    HStack {
                        Text("P&L ($)")
                        Spacer()
                        Text(pnl >= 0 ? "+\(pnl.asCurrency)" : pnl.asCurrency)
                            .foregroundStyle(pnl >= 0 ? .green : .red)
                            .fontWeight(.semibold)
                            .font(.body.monospacedDigit())
                    }
                    if let r = vm.computedR {
                        HStack {
                            Text("P&L (R)")
                            Spacer()
                            Text(String(format: r >= 0 ? "+%.2fR" : "%.2fR", r))
                                .foregroundStyle(r >= 0 ? .green : .orange)
                                .fontWeight(.semibold)
                                .font(.body.monospacedDigit())
                        }
                    }
                }
            }

            // Notes
            Section("Notes") {
                TextEditor(text: $vm.notes)
                    .frame(minHeight: 80)
            }

            // Tags
            Section("Tags (comma-separated)") {
                TextField("breakout, earnings, main-lane", text: $vm.tagsText)
            }

            // Validation error
            if let err = vm.validationError {
                Section {
                    Label(err, systemImage: "exclamationmark.triangle.fill")
                        .foregroundStyle(.orange)
                        .font(.caption)
                }
            }
        }
    }
}

// MARK: - Price row

private struct PriceRow: View {
    let label: String
    @Binding var text: String
    let placeholder: String

    var body: some View {
        HStack {
            Text(label)
            Spacer()
            TextField(placeholder, text: $text)
                .keyboardType(.decimalPad)
                .multilineTextAlignment(.trailing)
                .font(.body.monospacedDigit())
        }
    }
}

#Preview {
    JournalEditorView()
        .environmentObject(AppEnvironment.preview)
        .preferredColorScheme(.dark)
}
