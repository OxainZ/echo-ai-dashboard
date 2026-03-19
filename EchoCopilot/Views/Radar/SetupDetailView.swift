// Views/Radar/SetupDetailView.swift
// Echo Copilot — Full setup detail with grouped sections + action buttons

import SwiftUI

struct SetupDetailView: View {
    let setup: TickerSetup
    @EnvironmentObject private var env: AppEnvironment
    @State private var vm: SetupDetailViewModel?
    @State private var showingJournalSheet = false
    @State private var showingExplanation = false

    var body: some View {
        Group {
            if let vm = vm {
                DetailContent(vm: vm, showingJournalSheet: $showingJournalSheet, showingExplanation: $showingExplanation)
            } else {
                ProgressView()
            }
        }
        .navigationTitle(setup.symbol)
        .navigationBarTitleDisplayMode(.inline)
        .onAppear { buildVM() }
        .sheet(isPresented: $showingJournalSheet) {
            JournalEditorView(prefillTicker: setup.symbol)
                .environmentObject(env)
        }
        .sheet(isPresented: $showingExplanation) {
            if let vm = vm {
                ExplanationSheet(vm: vm)
            }
        }
    }

    private func buildVM() {
        guard vm == nil else { return }
        let settings = env.settingsRepository.load()
        vm = SetupDetailViewModel(
            setup: setup,
            rulesEvaluator: env.rulesEvaluator,
            explanationService: env.explanationService,
            copyTicketService: env.copyTicketService,
            clipboardService: env.clipboardService,
            settings: settings
        )
    }
}

// MARK: - Detail content

private struct DetailContent: View {
    @Bindable var vm: SetupDetailViewModel
    @Binding var showingJournalSheet: Bool
    @Binding var showingExplanation: Bool

    var body: some View {
        ScrollView {
            VStack(spacing: 14) {
                // Header badges
                headerSection

                // Action buttons
                actionButtons

                // Overview section
                SectionCardView(title: "Overview", systemImage: "info.circle") {
                    if let name = vm.setup.companyName {
                        MetricRowView(label: "Company", value: name)
                    }
                    MetricRowView(label: "Lane", value: vm.setup.lane.rawValue)
                    MetricRowView(label: "Cash", value: vm.setup.cashCompliance.rawValue)
                    MetricRowView(label: "Verified", value: vm.setup.isVerified ? "Yes" : "No",
                                  highlight: !vm.setup.isVerified, valueColor: .orange)
                    MetricRowView(label: "Halted", value: vm.setup.halted ? "YES" : "No",
                                  highlight: vm.setup.halted, valueColor: .red)
                    MetricRowView(label: "SSR", value: vm.setup.ssrActive ? "Active" : "No")
                    MetricRowView(label: "Updated", value: vm.setup.timestamp.asDateTimeString)
                }

                // Key levels
                SectionCardView(title: "Key Levels", systemImage: "target") {
                    MetricRowView(label: "Price", value: vm.setup.price.asPriceOrNA)
                    MetricRowView(label: "Prior Close", value: vm.setup.priorClose.asPriceOrNA)
                    MetricRowView(label: "PMH", value: vm.setup.pmh.asPrice)
                    MetricRowView(label: "PDH", value: vm.setup.pdh.asPrice)
                    MetricRowView(label: "PDL", value: vm.setup.pdl.asPriceOrNA)
                    Divider()
                    MetricRowView(label: "Trigger", value: vm.setup.trigger.asPriceOrNA,
                                  highlight: true, valueColor: .green)
                    MetricRowView(label: "Invalidation", value: vm.setup.invalidation.asPriceOrNA,
                                  highlight: true, valueColor: .red)
                    MetricRowView(label: "Target 1", value: vm.setup.target1.asPriceOrNA,
                                  highlight: true, valueColor: .cyan)
                    MetricRowView(label: "Target 2", value: vm.setup.target2.asPriceOrNA,
                                  highlight: true, valueColor: .cyan)
                }

                // Quality metrics
                SectionCardView(title: "Quality Metrics", systemImage: "chart.bar.fill") {
                    MetricRowView(label: "RVOL", value: vm.setup.rvol.asMultiplierOrNA,
                                  highlight: true, valueColor: rvolColor)
                    MetricRowView(label: "Vol-Z", value: vm.setup.volZ.asRounded2OrNA)
                    MetricRowView(label: "Spread", value: vm.setup.spreadPct.asPercentOrNA,
                                  highlight: true, valueColor: spreadColor)
                    MetricRowView(label: "Dollar Volume", value: vm.setup.dollarVolume.asShortDollarOrNA)
                    MetricRowView(label: "ADTV", value: vm.setup.adtvDollar.asShortDollarOrNA)
                    MetricRowView(label: "Impact % ADTV", value: vm.setup.impactPctADTV.asPercentOrNA,
                                  highlight: vm.setup.impactPctADTV != nil, valueColor: impactColor)
                }

                // Catalyst
                if let cat = vm.setup.catalystSummary, !cat.isEmpty {
                    SectionCardView(title: "Catalyst", systemImage: "bolt.fill") {
                        Text(cat)
                            .font(.subheadline)
                            .foregroundStyle(.primary)
                            .frame(maxWidth: .infinity, alignment: .leading)
                    }
                }

                // Notes
                if !vm.setup.notes.isEmpty {
                    SectionCardView(title: "Notes", systemImage: "note.text") {
                        Text(vm.setup.notes)
                            .font(.subheadline)
                            .foregroundStyle(.primary)
                            .frame(maxWidth: .infinity, alignment: .leading)
                    }
                }

                // Shadow reasons
                if vm.setup.status == .shadow {
                    SectionCardView(title: "Shadow Reasons", systemImage: "exclamationmark.triangle.fill") {
                        if vm.setup.shadowReasons.isEmpty {
                            Text("No shadow reasons recorded.")
                                .font(.subheadline)
                                .foregroundStyle(.secondary)
                        } else {
                            ForEach(vm.setup.shadowReasons, id: \.self) { reason in
                                HStack(spacing: 6) {
                                    Image(systemName: "xmark.circle.fill")
                                        .foregroundStyle(.orange)
                                        .font(.caption)
                                    Text(reason.description)
                                        .font(.subheadline)
                                }
                            }
                        }
                    }
                }

                // Pass/fail checklist
                if let eval = vm.evaluationResult {
                    SectionCardView(title: "Rules Checklist", systemImage: "checklist") {
                        ForEach(eval.passedChecks, id: \.self) { check in
                            CheckRow(text: check, passed: true)
                        }
                        ForEach(eval.failedChecks, id: \.self) { check in
                            CheckRow(text: check, passed: false)
                        }
                    }
                }

                // Ticket preview
                SectionCardView(title: "Ticket Preview", systemImage: "doc.text") {
                    Text(vm.ticketText)
                        .font(.system(size: 11, design: .monospaced))
                        .foregroundStyle(.secondary)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .textSelection(.enabled)
                }
            }
            .padding(16)
        }
    }

    // MARK: - Header badges

    private var headerSection: some View {
        HStack(spacing: 8) {
            StatusBadgeView(status: vm.setup.status)
            LaneBadgeView(lane: vm.setup.lane)
            ComplianceBadgeView(compliance: vm.setup.cashCompliance)
            Spacer()
            if let price = vm.setup.price {
                Text(price.asCurrency)
                    .font(.title3.bold().monospacedDigit())
            }
        }
        .padding(14)
        .background(Color(.systemGray6), in: RoundedRectangle(cornerRadius: 14))
    }

    // MARK: - Action buttons

    private var actionButtons: some View {
        VStack(spacing: 10) {
            HStack(spacing: 10) {
                CopyButtonView(
                    text: vm.ticketText,
                    label: "Copy Ticket",
                    icon: "doc.on.doc"
                )

                ShareLink(item: vm.ticketText) {
                    HStack(spacing: 6) {
                        Image(systemName: "square.and.arrow.up")
                        Text("Share")
                    }
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(.white)
                    .padding(.horizontal, 16)
                    .padding(.vertical, 10)
                    .background(Color(.systemGray4), in: RoundedRectangle(cornerRadius: 10))
                }
                .buttonStyle(.plain)

                Button {
                    showingJournalSheet = true
                } label: {
                    HStack(spacing: 6) {
                        Image(systemName: "book.closed")
                        Text("Journal This")
                    }
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(.white)
                    .padding(.horizontal, 16)
                    .padding(.vertical, 10)
                    .background(Color(.systemGray4), in: RoundedRectangle(cornerRadius: 10))
                }
                .buttonStyle(.plain)
            }

            HStack(spacing: 10) {
                Button {
                    showingExplanation = true
                    Task { await vm.explainSetup() }
                } label: {
                    HStack(spacing: 6) {
                        if vm.isExplaining {
                            ProgressView().tint(.white).scaleEffect(0.8)
                        } else {
                            Image(systemName: "sparkles")
                        }
                        Text("Explain Setup")
                    }
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(.white)
                    .padding(.horizontal, 16)
                    .padding(.vertical, 10)
                    .background(Color.indigo, in: RoundedRectangle(cornerRadius: 10))
                }
                .buttonStyle(.plain)

                Button {
                    vm.reEvaluate()
                } label: {
                    HStack(spacing: 6) {
                        Image(systemName: "arrow.clockwise")
                        Text("Re-evaluate")
                    }
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(.white)
                    .padding(.horizontal, 16)
                    .padding(.vertical, 10)
                    .background(Color(.systemGray4), in: RoundedRectangle(cornerRadius: 10))
                }
                .buttonStyle(.plain)
            }
        }
    }

    // MARK: - Derived colors

    private var rvolColor: Color {
        guard let rvol = vm.setup.rvol else { return .secondary }
        return rvol >= 2.0 ? .green : rvol >= 1.5 ? .yellow : .orange
    }

    private var spreadColor: Color {
        let threshold = vm.setup.lane == .main ? 0.35 : 0.25
        guard let spread = vm.setup.spreadPct else { return .secondary }
        return spread <= threshold ? .green : .red
    }

    private var impactColor: Color {
        let threshold = vm.setup.lane == .main ? 0.50 : 0.30
        guard let impact = vm.setup.impactPctADTV else { return .secondary }
        return impact <= threshold ? .green : .red
    }
}

// MARK: - Check row

private struct CheckRow: View {
    let text: String
    let passed: Bool

    var body: some View {
        HStack(spacing: 6) {
            Image(systemName: passed ? "checkmark.circle.fill" : "xmark.circle.fill")
                .font(.caption)
                .foregroundStyle(passed ? .green : .red)
            Text(text)
                .font(.caption)
                .foregroundStyle(.primary)
        }
    }
}

// MARK: - Explanation sheet

private struct ExplanationSheet: View {
    let vm: SetupDetailViewModel
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    if vm.isExplaining {
                        HStack {
                            Spacer()
                            ProgressView("Analyzing…")
                            Spacer()
                        }
                        .padding(.top, 40)
                    } else if let exp = vm.explanation {
                        VStack(alignment: .leading, spacing: 12) {
                            if exp.usedAI {
                                HStack(spacing: 4) {
                                    Image(systemName: "sparkles")
                                    Text("Apple Intelligence")
                                }
                                .font(.caption.weight(.semibold))
                                .foregroundStyle(.purple)
                            } else {
                                HStack(spacing: 4) {
                                    Image(systemName: "function")
                                    Text("Rules-Based Analysis")
                                }
                                .font(.caption.weight(.semibold))
                                .foregroundStyle(.secondary)
                            }

                            Text(exp.headline)
                                .font(.headline)

                            Text(exp.body)
                                .font(.body)
                                .foregroundStyle(.secondary)

                            if !exp.passedChecks.isEmpty {
                                Text("Passed Checks")
                                    .font(.subheadline.weight(.semibold))
                                    .padding(.top, 4)
                                ForEach(exp.passedChecks, id: \.self) { c in
                                    Label(c, systemImage: "checkmark.circle.fill")
                                        .font(.caption)
                                        .foregroundStyle(.green)
                                }
                            }

                            if !exp.failedChecks.isEmpty {
                                Text("Failed Checks")
                                    .font(.subheadline.weight(.semibold))
                                    .padding(.top, 4)
                                ForEach(exp.failedChecks, id: \.self) { c in
                                    Label(c, systemImage: "xmark.circle.fill")
                                        .font(.caption)
                                        .foregroundStyle(.red)
                                }
                            }

                            Divider()

                            Label(exp.riskNote, systemImage: "exclamationmark.shield")
                                .font(.footnote)
                                .foregroundStyle(.orange)
                        }
                    } else {
                        EmptyStateView(
                            systemImage: "sparkles",
                            title: "No Explanation Yet",
                            subtitle: "Tap Explain Setup on the detail screen."
                        )
                    }
                }
                .padding(20)
            }
            .navigationTitle("Setup Explanation")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button("Done") { dismiss() }
                }
            }
        }
    }
}

#Preview {
    NavigationStack {
        SetupDetailView(setup: TickerSetup.previewActionable)
            .environmentObject(AppEnvironment.preview)
            .preferredColorScheme(.dark)
    }
}
