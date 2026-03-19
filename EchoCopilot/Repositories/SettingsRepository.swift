// Repositories/SettingsRepository.swift
// Echo Copilot — AppSettings persistence via UserDefaults + Codable

import Foundation

// MARK: - Protocol

protocol SettingsRepositoryProtocol {
    func load() -> AppSettings
    func save(_ settings: AppSettings)
    func reset()
}

// MARK: - UserDefaults implementation

final class UserDefaultsSettingsRepository: SettingsRepositoryProtocol {
    private let key = "echo_app_settings"
    private let defaults: UserDefaults

    init(defaults: UserDefaults = .standard) {
        self.defaults = defaults
    }

    func load() -> AppSettings {
        guard let data = defaults.data(forKey: key),
              let settings = try? JSONDecoder().decode(AppSettings.self, from: data) else {
            return AppSettings()
        }
        return settings
    }

    func save(_ settings: AppSettings) {
        guard let data = try? JSONEncoder().encode(settings) else { return }
        defaults.set(data, forKey: key)
    }

    func reset() {
        defaults.removeObject(forKey: key)
    }
}
