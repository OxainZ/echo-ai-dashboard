// Views/Radar/SetupEditorView.swift
// Echo Copilot — Sheet for creating or editing a TickerSetup

import SwiftUI

struct SetupEditorView: View {
    var editing: TickerSetup? = nil

    @EnvironmentObject private var env: AppEnvironment
    @Environment(\.dismiss) private var dismiss
    @State private var vm: SetupEditorViewModel?
    @State private var isSaving = false

    var body: some View {
        NavigationStack {
            Group {
                if let vm {
                    EditorForm(vm: vm)
                } else {
                    ProgressView()
                }
            }
            .navigationTitle(editing == nil ? "New Setup" : "Edit Setup")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    Button("Cancel") { dismiss() }
                }
                ToolbarItem(placement: .topBarTrailing) {
                    Button("Save") { saveAndDismiss() }
                        .fontWeight(.semibold)
                        .disabled(vm?.canSave != true || isSaving)
                }
            }
        }
        .onAppear {
            vm = SetupEditorViewModel(editing: editing, repository: env.setupRepository)
        }
    }

    private func saveAndDismiss() {
        guard let vm else { return }
        isSaving = true
        Task {
            try? await vm.save()
            await MainActor.run { dismiss() }
        }
    }
}

// MARK: - Form

private struct EditorForm: View {
    @Bindable var vm: SetupEditorViewModel

    var body: some View {
        Form {
            // Identity
            Section("Setup") {
                HStack {
                    Text("Symbol *")
                    Spacer()
                    TextField("NVDA", text: $vm.symbol)
                        .multilineTextAlignment(.trailing)
                        .textCase(.uppercase)
                        .autocorrectionDisabled()
                }
                HStack {
                    Text("Company")
                    Spacer()
                    TextField("Optional", text: $vm.companyName)
                        .multilineTextAlignment(.trailing)
                }
                Picker("Lane", selection: $vm.lane) {
                    ForEach(TradingLane.allCases, id: \.self) { Text($0.rawValue).tag($0) }
                }
                .pickerStyle(.segmented)

                Picker("Cash Compliance", selection: $vm.cashCompliance) {
                    ForEach(CashCompliance.allCases, id: \.self) { Text($0.rawValue).tag($0) }
                }
            }

            // Status flags
            Section("Status") {
                Toggle("Verified", isOn: $vm.isVerified)
                Toggle("Halted", isOn: $vm.halted)
                Toggle("SSR Active", isOn: $vm.ssrActive)
            }

            // Key levels
            Section("Key Levels") {
                PriceField("Price", text: $vm.priceText)
                PriceField("Prior Close", text: $vm.priorCloseText)
                PriceField("PMH (Pre-Market High)", text: $vm.pmhText)
                PriceField("PDH (Prior Day High)", text: $vm.pdhText)
                PriceField("PDL (Prior Day Low)", text: $vm.pdlText)
            }

            // Levels
            Section("Trade Levels") {
                PriceField("Trigger", text: $vm.triggerText)
                PriceField("Invalidation", text: $vm.invalidationText)
                PriceField("Target 1", text: $vm.target1Text)
                PriceField("Target 2", text: $vm.target2Text)
            }

            // Metrics
            Section("Quality Metrics") {
                PriceField("RVOL (e.g. 2.5)", text: $vm.rvolText)
                PriceField("Vol-Z (e.g. 1.8)", text: $vm.volZText)
                PriceField("Spread % (e.g. 0.12)", text: $vm.spreadPctText)
                PriceField("Impact % ADTV (e.g. 0.30)", text: $vm.impactPctText)
            }

            // Catalyst + Notes
            Section("Catalyst") {
                TextField("Earnings beat, upgrade, etc.", text: $vm.catalystSummary, axis: .vertical)
                    .lineLimit(3, reservesSpace: true)
            }

            Section("Notes") {
                TextField("Observations, plan, etc.", text: $vm.notes, axis: .vertical)
                    .lineLimit(4, reservesSpace: true)
            }

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

// MARK: - Helper

private struct PriceField: View {
    let label: String
    @Binding var text: String

    init(_ label: String, text: Binding<String>) {
        self.label = label
        self._text = text
    }

    var body: some View {
        HStack {
            Text(label)
            Spacer()
            TextField("0.00", text: $text)
                .keyboardType(.decimalPad)
                .multilineTextAlignment(.trailing)
                .font(.body.monospacedDigit())
                .frame(width: 100)
        }
    }
}

#Preview {
    SetupEditorView()
        .environmentObject(AppEnvironment.preview)
        .preferredColorScheme(.dark)
}
