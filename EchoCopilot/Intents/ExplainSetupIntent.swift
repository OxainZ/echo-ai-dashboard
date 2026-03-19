// Intents/ExplainSetupIntent.swift
// Echo Copilot — App Intent: explain a setup for a given ticker symbol

import AppIntents

struct ExplainSetupIntent: AppIntent {
    static let title: LocalizedStringResource = "Explain Setup"
    static let description = IntentDescription("Returns a plain-English explanation of the trading setup for the given ticker.")

    @Parameter(title: "Ticker Symbol")
    var ticker: String

    func perform() async throws -> some ProvidesDialog {
        let repo = UserDefaultsSetupRepository()
        let setups = try await repo.fetchSetups()

        guard let setup = setups.first(where: { $0.symbol.uppercased() == ticker.uppercased() }) else {
            return .result(dialog: "No setup found for \(ticker).")
        }

        let evaluator = SetupRulesEvaluator()
        let eval = evaluator.evaluate(setup: setup, settings: AppSettings())
        let service = DeterministicExplanationService()
        let explanation = await service.explain(setup: setup, evaluation: eval)

        return .result(dialog: "\(explanation.headline). \(explanation.body)")
    }
}
