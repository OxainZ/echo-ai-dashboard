// Views/Settings/SettingsView.swift
// Echo Copilot — Settings: all editable preferences with live persistence

import SwiftUI

struct SettingsView: View {
    @EnvironmentObject private var env: AppEnvironment
    @State private var vm: SettingsViewModel?
    @State private var showResetConfirm = false

    var body: some View {
        NavigationStack {
            Group {
                if let vm = vm {
                    SettingsForm(vm: vm, showResetConfirm: $showResetConfirm)
                } else {
                    ProgressView()
                }
            }
            .navigationTitle("Settings")
            .navigationBarTitleDisplayMode(.large)
        }
        .onAppear {
            if vm == nil {
                vm = SettingsViewModel(repository: env.settingsRepository)
            }
        }
        .confirmationDialog("Reset Settings", isPresented: $showResetConfirm) {
            Button("Reset to Defaults", role: .destructive) {
                vm?.resetSettings()
            }
        } message: {
            Text("All settings will be reset to their default values.")
        }
    }
}

private struct SettingsForm: View {
    @Bindable var vm: SettingsViewModel
    @Binding var showResetConfirm: Bool

    var body: some View {
        Form {
            // Data source
            Section("Data Source") {
                Toggle("Use Mock Data", isOn: $vm.settings.useMockData)
                    .onChange(of: vm.settings.useMockData) { _, _ in vm.save() }
            }

            // Lane thresholds
            Section("Lane Thresholds") {
                SliderRow(
                    label: "Main Lane Spread ≤",
                    value: $vm.settings.mainLaneSpreadThreshold,
                    range: 0.05...2.0,
                    step: 0.05,
                    format: "%.2f%%"
                ) { vm.save() }

                SliderRow(
                    label: "Micro Lane Spread ≤",
                    value: $vm.settings.microLaneSpreadThreshold,
                    range: 0.05...2.0,
                    step: 0.05,
                    format: "%.2f%%"
                ) { vm.save() }

                SliderRow(
                    label: "Main Impact ≤",
                    value: $vm.settings.impactThresholdMain,
                    range: 0.1...5.0,
                    step: 0.05,
                    format: "%.2f%%"
                ) { vm.save() }

                SliderRow(
                    label: "Micro Impact ≤",
                    value: $vm.settings.impactThresholdMicro,
                    range: 0.1...5.0,
                    step: 0.05,
                    format: "%.2f%%"
                ) { vm.save() }
            }

            // Volume quality
            Section("Volume Quality") {
                SliderRow(
                    label: "RVOL Threshold ≥",
                    value: $vm.settings.rvolThreshold,
                    range: 0.5...5.0,
                    step: 0.1,
                    format: "%.1fx"
                ) { vm.save() }

                SliderRow(
                    label: "Vol-Z Threshold ≥",
                    value: $vm.settings.volZThreshold,
                    range: 0.0...4.0,
                    step: 0.1,
                    format: "%.1f"
                ) { vm.save() }
            }

            // Risk sizing
            Section("Risk Sizing") {
                SliderRow(
                    label: "Default Risk %",
                    value: $vm.settings.defaultRiskPercent,
                    range: 0.1...5.0,
                    step: 0.1,
                    format: "%.1f%%"
                ) { vm.save() }
            }

            // Display
            Section("Display") {
                Toggle("Show Micro Lane", isOn: $vm.settings.showMicroLane)
                    .onChange(of: vm.settings.showMicroLane) { _, _ in vm.save() }

                Picker("Default Sort", selection: $vm.settings.preferredSortOption) {
                    ForEach(SortOption.allCases) { opt in
                        Text(opt.rawValue).tag(opt)
                    }
                }
                .onChange(of: vm.settings.preferredSortOption) { _, _ in vm.save() }
            }

            // AI features
            Section("AI Features") {
                Toggle("Enable Foundation Models", isOn: $vm.settings.enableFoundationModels)
                    .onChange(of: vm.settings.enableFoundationModels) { _, _ in vm.save() }
                Text("Uses Apple Intelligence for setup explanations when available (iOS 26+). Falls back to rules-based text on unsupported devices.")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }

            // Reset
            Section("Data") {
                Button(role: .destructive) {
                    showResetConfirm = true
                } label: {
                    Label("Reset All Settings", systemImage: "arrow.counterclockwise")
                }
            }
        }
    }
}

// MARK: - Slider row

private struct SliderRow: View {
    let label: String
    @Binding var value: Double
    let range: ClosedRange<Double>
    let step: Double
    let format: String
    let onChange: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            HStack {
                Text(label)
                    .font(.subheadline)
                Spacer()
                Text(String(format: format, value))
                    .font(.subheadline.monospacedDigit())
                    .foregroundStyle(.accent)
                    .frame(minWidth: 60, alignment: .trailing)
            }
            Slider(value: $value, in: range, step: step)
                .onChange(of: value) { _, _ in onChange() }
        }
    }
}

#Preview {
    SettingsView()
        .environmentObject(AppEnvironment.preview)
        .preferredColorScheme(.dark)
}
