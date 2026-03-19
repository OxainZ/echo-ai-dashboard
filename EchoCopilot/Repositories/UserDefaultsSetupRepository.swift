// Repositories/UserDefaultsSetupRepository.swift
// Echo Copilot — Persistent setup storage via UserDefaults JSON.
// Use this for personal use: setups survive app restarts.

import Foundation

final class UserDefaultsSetupRepository: SetupRepositoryProtocol {
    private let key = "echoSetups_v1"
    private let defaults: UserDefaults

    init(defaults: UserDefaults = .standard) {
        self.defaults = defaults
    }

    // MARK: - Fetch

    func fetchSetups() async throws -> [TickerSetup] {
        return load()
    }

    func refresh() async throws -> [TickerSetup] {
        return load()
    }

    // MARK: - Mutate

    func save(_ setup: TickerSetup) async throws {
        var all = load()
        if let idx = all.firstIndex(where: { $0.id == setup.id }) {
            all[idx] = setup
        } else {
            all.insert(setup, at: 0)
        }
        try persist(all)
    }

    func delete(id: UUID) async throws {
        var all = load()
        all.removeAll { $0.id == id }
        try persist(all)
    }

    // MARK: - Helpers

    private func load() -> [TickerSetup] {
        guard let data = defaults.data(forKey: key) else { return SampleSetups.all }
        return (try? JSONDecoder().decode([TickerSetup].self, from: data)) ?? SampleSetups.all
    }

    private func persist(_ setups: [TickerSetup]) throws {
        let data = try JSONEncoder().encode(setups)
        defaults.set(data, forKey: key)
    }
}
