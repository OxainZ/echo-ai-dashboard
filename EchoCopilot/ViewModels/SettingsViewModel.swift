// ViewModels/SettingsViewModel.swift
// Echo Copilot — Settings form state with live persistence

import Foundation
import Observation

@Observable
final class SettingsViewModel {
    var settings: AppSettings

    private let repository: any SettingsRepositoryProtocol

    init(repository: any SettingsRepositoryProtocol) {
        self.repository = repository
        self.settings = repository.load()
    }

    // MARK: - Save

    func save() {
        repository.save(settings)
    }

    // MARK: - Reset to defaults

    func resetSettings() {
        repository.reset()
        settings = AppSettings()
    }
}
