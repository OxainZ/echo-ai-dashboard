// Repositories/SetupRepository.swift
// Echo Copilot — Setup data source abstraction + mock implementation

import Foundation

// MARK: - Protocol

protocol SetupRepositoryProtocol {
    func fetchSetups() async throws -> [TickerSetup]
    func refresh() async throws -> [TickerSetup]
}

// MARK: - Mock (in-memory) implementation

final class MockSetupRepository: SetupRepositoryProtocol {
    private var setups: [TickerSetup]

    init(setups: [TickerSetup] = SampleSetups.all) {
        self.setups = setups
    }

    func fetchSetups() async throws -> [TickerSetup] {
        // Simulate a brief async fetch delay
        try await Task.sleep(nanoseconds: 200_000_000)
        return setups
    }

    func refresh() async throws -> [TickerSetup] {
        // In a real implementation, hit the backend here
        return try await fetchSetups()
    }
}
