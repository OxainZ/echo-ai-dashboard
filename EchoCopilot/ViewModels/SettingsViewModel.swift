// ViewModels/SettingsViewModel.swift
// Echo Copilot — Settings form state with live persistence

import Foundation
import Observation

@Observable
final class SettingsViewModel {
    var settings: AppSettings

    // Polygon API key is stored in Keychain, not AppSettings/UserDefaults
    var polygonApiKey: String {
        didSet { KeychainService.set(polygonApiKey, forKey: KeychainService.Key.polygonApiKey) }
    }

    private let repository: any SettingsRepositoryProtocol

    init(repository: any SettingsRepositoryProtocol) {
        self.repository = repository
        self.settings = repository.load()
        self.polygonApiKey = KeychainService.get(forKey: KeychainService.Key.polygonApiKey) ?? ""
    }

    // MARK: - Save

    func save() {
        repository.save(settings)
    }

    // MARK: - Reset to defaults

    func resetSettings() {
        repository.reset()
        settings = AppSettings()
        polygonApiKey = ""
        KeychainService.delete(forKey: KeychainService.Key.polygonApiKey)
    }
}
