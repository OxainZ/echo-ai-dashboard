// Repositories/SetupRepository.swift
// Echo Copilot — Setup data source abstraction + mock implementation

import Foundation

// MARK: - Protocol

protocol SetupRepositoryProtocol {
    func fetchSetups() async throws -> [TickerSetup]
    func refresh() async throws -> [TickerSetup]
    func save(_ setup: TickerSetup) async throws
    func delete(id: UUID) async throws
}

// MARK: - Mock (in-memory) implementation

final class MockSetupRepository: SetupRepositoryProtocol {
    private var setups: [TickerSetup]

    init(setups: [TickerSetup] = SampleSetups.all) {
        self.setups = setups
    }

    func fetchSetups() async throws -> [TickerSetup] {
        try await Task.sleep(nanoseconds: 200_000_000)
        return setups
    }

    func refresh() async throws -> [TickerSetup] {
        return try await fetchSetups()
    }

    func save(_ setup: TickerSetup) async throws {
        if let idx = setups.firstIndex(where: { $0.id == setup.id }) {
            setups[idx] = setup
        } else {
            setups.insert(setup, at: 0)
        }
    }

    func delete(id: UUID) async throws {
        setups.removeAll { $0.id == id }
    }
}
