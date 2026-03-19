// App/AppEnvironment.swift
// Echo Copilot — Dependency container. Inject via .environmentObject(AppEnvironment()).

import Foundation

@MainActor
final class AppEnvironment: ObservableObject {
    let setupRepository: any SetupRepositoryProtocol
    let journalRepository: any JournalRepositoryProtocol
    let settingsRepository: any SettingsRepositoryProtocol
    let rulesEvaluator: any RulesEvaluationServiceProtocol
    let explanationService: any ExplanationServiceProtocol
    let clipboardService: any ClipboardServiceProtocol
    let copyTicketService: CopyTicketService

    init(
        setupRepository: (any SetupRepositoryProtocol)? = nil,
        journalRepository: (any JournalRepositoryProtocol)? = nil,
        settingsRepository: (any SettingsRepositoryProtocol)? = nil,
        rulesEvaluator: (any RulesEvaluationServiceProtocol)? = nil,
        explanationService: (any ExplanationServiceProtocol)? = nil,
        clipboardService: (any ClipboardServiceProtocol)? = nil
    ) {
        let settingsRepo = settingsRepository ?? UserDefaultsSettingsRepository()
        let settings = settingsRepo.load()

        self.settingsRepository = settingsRepo
        self.setupRepository = setupRepository ?? MockSetupRepository()
        self.journalRepository = journalRepository ?? UserDefaultsJournalRepository()
        self.rulesEvaluator = rulesEvaluator ?? SetupRulesEvaluator()
        self.explanationService = explanationService ?? ExplanationServiceFactory.make(enableAI: settings.enableFoundationModels)
        self.clipboardService = clipboardService ?? LiveClipboardService()
        self.copyTicketService = CopyTicketService()
    }
}
