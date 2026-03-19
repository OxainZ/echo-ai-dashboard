// Repositories/JournalRepository.swift
// Echo Copilot — Journal persistence via UserDefaults + Codable

import Foundation

// MARK: - Protocol

protocol JournalRepositoryProtocol {
    func fetchEntries() throws -> [JournalEntry]
    func save(entry: JournalEntry) throws
    func delete(id: UUID) throws
    func update(entry: JournalEntry) throws
}

// MARK: - UserDefaults implementation

final class UserDefaultsJournalRepository: JournalRepositoryProtocol {
    private let key = "echo_journal_entries"
    private let defaults: UserDefaults

    init(defaults: UserDefaults = .standard) {
        self.defaults = defaults
    }

    func fetchEntries() throws -> [JournalEntry] {
        guard let data = defaults.data(forKey: key) else { return [] }
        return try JSONDecoder().decode([JournalEntry].self, from: data)
    }

    func save(entry: JournalEntry) throws {
        var entries = (try? fetchEntries()) ?? []
        entries.insert(entry, at: 0) // newest first
        try persist(entries)
    }

    func delete(id: UUID) throws {
        var entries = (try? fetchEntries()) ?? []
        entries.removeAll { $0.id == id }
        try persist(entries)
    }

    func update(entry: JournalEntry) throws {
        var entries = (try? fetchEntries()) ?? []
        if let idx = entries.firstIndex(where: { $0.id == entry.id }) {
            entries[idx] = entry
        } else {
            entries.insert(entry, at: 0)
        }
        try persist(entries)
    }

    // MARK: - Private

    private func persist(_ entries: [JournalEntry]) throws {
        let data = try JSONEncoder().encode(entries)
        defaults.set(data, forKey: key)
    }
}
