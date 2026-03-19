// ViewModels/SettingsViewModel.swift
// Echo Copilot — Settings form state with live persistence

import Foundation
import Observation

@Observable
final class SettingsViewModel {
    var settings: AppSettings
    var exportURL: URLWrapper? = nil

    // Polygon API key is stored in Keychain, not AppSettings/UserDefaults
    var polygonApiKey: String {
        didSet { KeychainService.set(polygonApiKey, forKey: KeychainService.Key.polygonApiKey) }
    }

    private let repository: any SettingsRepositoryProtocol
    private let setupRepository: any SetupRepositoryProtocol

    init(repository: any SettingsRepositoryProtocol,
         setupRepository: any SetupRepositoryProtocol) {
        self.repository = repository
        self.setupRepository = setupRepository
        self.settings = repository.load()
        self.polygonApiKey = KeychainService.get(forKey: KeychainService.Key.polygonApiKey) ?? ""
    }

    // MARK: - Save

    func save() {
        repository.save(settings)
    }

    // MARK: - Export

    func exportSetups() {
        Task {
            guard let setups = try? await setupRepository.fetchSetups(),
                  let url = try? ExportService.setupsJSON(setups) else { return }
            await MainActor.run { exportURL = URLWrapper(url: url) }
        }
    }

    // MARK: - Reset to defaults

    func resetSettings() {
        repository.reset()
        settings = AppSettings()
        polygonApiKey = ""
        KeychainService.delete(forKey: KeychainService.Key.polygonApiKey)
    }
}

/// Identifiable wrapper so a URL can drive a `.sheet(item:)`.
struct URLWrapper: Identifiable {
    let id = UUID()
    let url: URL
}
