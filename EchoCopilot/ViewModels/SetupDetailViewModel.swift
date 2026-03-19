// ViewModels/SetupDetailViewModel.swift
// Echo Copilot — Setup detail screen state: re-evaluate, explain, copy ticket

import Foundation
import Observation

@Observable
final class SetupDetailViewModel {
    // MARK: - State

    var setup: TickerSetup
    var evaluationResult: SetupEvaluationResult?
    var explanation: ExplanationResult?
    var isExplaining: Bool = false
    var copiedTicket: Bool = false

    // MARK: - Dependencies

    private let rulesEvaluator: any RulesEvaluationServiceProtocol
    private let explanationService: any ExplanationServiceProtocol
    private let copyTicketService: CopyTicketService
    private let clipboardService: any ClipboardServiceProtocol
    private let settings: AppSettings

    init(
        setup: TickerSetup,
        rulesEvaluator: any RulesEvaluationServiceProtocol,
        explanationService: any ExplanationServiceProtocol,
        copyTicketService: CopyTicketService,
        clipboardService: any ClipboardServiceProtocol,
        settings: AppSettings
    ) {
        self.setup = setup
        self.rulesEvaluator = rulesEvaluator
        self.explanationService = explanationService
        self.copyTicketService = copyTicketService
        self.clipboardService = clipboardService
        self.settings = settings

        // Run initial evaluation
        self.evaluationResult = rulesEvaluator.evaluate(setup: setup, settings: settings)
    }

    // MARK: - Actions

    func reEvaluate() {
        evaluationResult = rulesEvaluator.evaluate(setup: setup, settings: settings)
    }

    func explainSetup() async {
        guard let eval = evaluationResult else { return }
        isExplaining = true
        explanation = await explanationService.explain(setup: setup, evaluation: eval)
        isExplaining = false
    }

    func copyTicket() {
        let text = copyTicketService.ticketText(for: setup)
        clipboardService.copy(text)
        copiedTicket = true
        Task { @MainActor in
            try? await Task.sleep(nanoseconds: 2_000_000_000)
            copiedTicket = false
        }
    }

    var ticketText: String {
        copyTicketService.ticketText(for: setup)
    }
}
