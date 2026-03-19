// ViewModels/JournalEditorViewModel.swift
// Echo Copilot — Add / edit journal entry form state + validation

import Foundation
import Observation

@Observable
final class JournalEditorViewModel {
    // MARK: - Form fields

    var ticker: String = ""
    var entryDate: Date = Date()
    var hasExitDate: Bool = false
    var exitDate: Date = Date()
    var entryPriceText: String = ""
    var hasExitPrice: Bool = false
    var exitPriceText: String = ""
    var hasStopPrice: Bool = false
    var stopPriceText: String = ""
    var hasTarget1: Bool = false
    var target1Text: String = ""
    var hasTarget2: Bool = false
    var target2Text: String = ""
    var notes: String = ""
    var tagsText: String = ""    // Comma-separated

    var isEditing: Bool = false
    private var editingId: UUID?

    private let repository: any JournalRepositoryProtocol

    init(repository: any JournalRepositoryProtocol) {
        self.repository = repository
    }

    // MARK: - Load existing entry for editing

    func load(entry: JournalEntry) {
        isEditing = true
        editingId = entry.id
        ticker = entry.ticker
        entryDate = entry.entryDate
        entryPriceText = entry.entryPrice.asPrice

        if let exit = entry.exitDate {
            hasExitDate = true
            exitDate = exit
        }
        if let exit = entry.exitPrice {
            hasExitPrice = true
            exitPriceText = exit.asPrice
        }
        if let stop = entry.stopPrice {
            hasStopPrice = true
            stopPriceText = stop.asPrice
        }
        if let t1 = entry.target1 {
            hasTarget1 = true
            target1Text = t1.asPrice
        }
        if let t2 = entry.target2 {
            hasTarget2 = true
            target2Text = t2.asPrice
        }
        notes = entry.notes
        tagsText = entry.tags.joined(separator: ", ")
    }

    // MARK: - Validation

    var validationError: String? {
        if ticker.trimmingCharacters(in: .whitespaces).isEmpty { return "Ticker is required" }
        if Double(entryPriceText) == nil || (Double(entryPriceText) ?? 0) <= 0 {
            return "Valid entry price is required"
        }
        return nil
    }

    var canSave: Bool { validationError == nil }

    // MARK: - Save

    @discardableResult
    func save() throws -> Bool {
        guard canSave else { return false }

        let entry = JournalEntry(
            id: editingId ?? UUID(),
            ticker: ticker.uppercased().trimmingCharacters(in: .whitespaces),
            entryDate: entryDate,
            exitDate: hasExitDate ? exitDate : nil,
            entryPrice: Double(entryPriceText) ?? 0,
            exitPrice: hasExitPrice ? Double(exitPriceText) : nil,
            stopPrice: hasStopPrice ? Double(stopPriceText) : nil,
            target1: hasTarget1 ? Double(target1Text) : nil,
            target2: hasTarget2 ? Double(target2Text) : nil,
            notes: notes,
            tags: tagsText.split(separator: ",").map { $0.trimmingCharacters(in: .whitespaces) }
        )

        if isEditing {
            try repository.update(entry: entry)
        } else {
            try repository.save(entry: entry)
        }
        return true
    }

    // MARK: - Computed preview

    var computedPnL: Double? {
        guard let entry = Double(entryPriceText),
              hasExitPrice,
              let exit = Double(exitPriceText) else { return nil }
        return exit - entry
    }

    var computedR: Double? {
        guard let entry = Double(entryPriceText),
              hasExitPrice, let exit = Double(exitPriceText),
              hasStopPrice, let stop = Double(stopPriceText) else { return nil }
        let risk = abs(entry - stop)
        guard risk > 0 else { return nil }
        return (exit - entry) / risk
    }
}
