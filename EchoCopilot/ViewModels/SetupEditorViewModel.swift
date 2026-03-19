// ViewModels/SetupEditorViewModel.swift
// Echo Copilot — Create or edit a TickerSetup

import Foundation
import Observation

@Observable
final class SetupEditorViewModel {
    // MARK: - Editable fields

    var symbol: String = ""
    var companyName: String = ""
    var lane: TradingLane = .main
    var cashCompliance: CashCompliance = .cashOK
    var isVerified: Bool = false
    var halted: Bool = false
    var ssrActive: Bool = false
    var catalystSummary: String = ""
    var notes: String = ""

    // Price level text fields
    var priceText: String = ""
    var priorCloseText: String = ""
    var pmhText: String = ""
    var pdhText: String = ""
    var pdlText: String = ""
    var triggerText: String = ""
    var invalidationText: String = ""
    var target1Text: String = ""
    var target2Text: String = ""

    // Metric text fields
    var rvolText: String = ""
    var volZText: String = ""
    var spreadPctText: String = ""
    var impactPctText: String = ""

    // MARK: - State

    var validationError: String? = nil
    private let editingID: UUID?
    private let repository: any SetupRepositoryProtocol

    init(editing setup: TickerSetup? = nil, repository: any SetupRepositoryProtocol) {
        self.repository = repository
        self.editingID = setup?.id
        if let s = setup { load(from: s) }
    }

    // MARK: - Validation

    var canSave: Bool { !symbol.trimmingCharacters(in: .whitespaces).isEmpty }

    // MARK: - Save

    func save() async throws {
        guard canSave else {
            validationError = "Symbol is required."
            return
        }

        let setup = TickerSetup(
            id: editingID ?? UUID(),
            symbol: symbol.uppercased().trimmingCharacters(in: .whitespaces),
            companyName: companyName.isEmpty ? nil : companyName,
            lane: lane,
            status: .shadow,   // will be re-evaluated by rules engine
            price: Double(priceText),
            priorClose: Double(priorCloseText),
            pmh: Double(pmhText) ?? 0,
            pdh: Double(pdhText) ?? 0,
            pdl: Double(pdlText),
            trigger: Double(triggerText),
            invalidation: Double(invalidationText),
            target1: Double(target1Text),
            target2: Double(target2Text),
            spreadPct: Double(spreadPctText),
            rvol: Double(rvolText),
            volZ: Double(volZText),
            impactPctADTV: Double(impactPctText),
            halted: halted,
            ssrActive: ssrActive,
            cashCompliance: cashCompliance,
            timestamp: Date(),
            notes: notes,
            catalystSummary: catalystSummary.isEmpty ? nil : catalystSummary,
            shadowReasons: [],
            isVerified: isVerified
        )

        try await repository.save(setup)
    }

    // MARK: - Load existing

    private func load(from s: TickerSetup) {
        symbol = s.symbol
        companyName = s.companyName ?? ""
        lane = s.lane
        cashCompliance = s.cashCompliance
        isVerified = s.isVerified
        halted = s.halted
        ssrActive = s.ssrActive
        catalystSummary = s.catalystSummary ?? ""
        notes = s.notes
        priceText = s.price.map { String(format: "%.2f", $0) } ?? ""
        priorCloseText = s.priorClose.map { String(format: "%.2f", $0) } ?? ""
        pmhText = String(format: "%.2f", s.pmh)
        pdhText = String(format: "%.2f", s.pdh)
        pdlText = s.pdl.map { String(format: "%.2f", $0) } ?? ""
        triggerText = s.trigger.map { String(format: "%.2f", $0) } ?? ""
        invalidationText = s.invalidation.map { String(format: "%.2f", $0) } ?? ""
        target1Text = s.target1.map { String(format: "%.2f", $0) } ?? ""
        target2Text = s.target2.map { String(format: "%.2f", $0) } ?? ""
        rvolText = s.rvol.map { String(format: "%.2f", $0) } ?? ""
        volZText = s.volZ.map { String(format: "%.2f", $0) } ?? ""
        spreadPctText = s.spreadPct.map { String(format: "%.3f", $0) } ?? ""
        impactPctText = s.impactPctADTV.map { String(format: "%.2f", $0) } ?? ""
    }
}
