// ViewModels/JournalListViewModel.swift
// Echo Copilot — Journal list: fetch, delete, stats summary

import Foundation
import Observation

@Observable
final class JournalListViewModel {
    var entries: [JournalEntry] = []
    var errorMessage: String? = nil

    private let repository: any JournalRepositoryProtocol

    init(repository: any JournalRepositoryProtocol) {
        self.repository = repository
    }

    // MARK: - Load

    func load() {
        do {
            entries = try repository.fetchEntries()
        } catch {
            errorMessage = "Failed to load journal: \(error.localizedDescription)"
        }
    }

    // MARK: - Delete

    /// Safe delete using explicit source array so section-based lists pass the
    /// correct entries (ForEach gives indices relative to its own array, not entries).
    func delete(from source: [JournalEntry], at offsets: IndexSet) {
        offsets.forEach { idx in
            try? repository.delete(id: source[idx].id)
        }
        load()
    }

    // MARK: - Close trade

    func close(entry: JournalEntry, exitPrice: Double, exitDate: Date = Date()) {
        var updated = entry
        updated.exitPrice = exitPrice
        updated.exitDate = exitDate
        try? repository.update(entry: updated)
        load()
    }

    // MARK: - Stats

    var closedTrades: [JournalEntry] { entries.filter { $0.exitPrice != nil } }
    var openTrades:   [JournalEntry] { entries.filter { $0.exitPrice == nil } }

    var totalPnL: Double {
        closedTrades.compactMap { $0.pnlDollars }.reduce(0, +)
    }

    var averageR: Double? {
        let rs = closedTrades.compactMap { $0.pnlR }
        guard !rs.isEmpty else { return nil }
        return rs.reduce(0, +) / Double(rs.count)
    }

    var winRate: Double? {
        let closed = closedTrades
        guard !closed.isEmpty else { return nil }
        let winners = closed.filter { ($0.pnlDollars ?? 0) > 0 }
        return Double(winners.count) / Double(closed.count)
    }
}
