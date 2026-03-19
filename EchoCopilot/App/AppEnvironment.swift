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
        self.journalRepository = journalRepository ?? UserDefaultsJournalRepository()
        self.rulesEvaluator = rulesEvaluator ?? SetupRulesEvaluator()
        self.explanationService = explanationService ?? ExplanationServiceFactory.make(enableAI: settings.enableFoundationModels)
        self.clipboardService = clipboardService ?? LiveClipboardService()
        self.copyTicketService = CopyTicketService()

        // Setup repository: use Polygon-enriched live data when an API key is set,
        // otherwise fall back to UserDefaults-persisted setups (seeded with sample data).
        if let overrideRepo = setupRepository {
            self.setupRepository = overrideRepo
        } else {
            let persistentRepo = UserDefaultsSetupRepository()
            if !settings.polygonApiKey.isEmpty {
                self.setupRepository = PolygonSetupRepository(base: persistentRepo, apiKey: settings.polygonApiKey)
            } else {
                self.setupRepository = persistentRepo
            }
        }
    }
}
