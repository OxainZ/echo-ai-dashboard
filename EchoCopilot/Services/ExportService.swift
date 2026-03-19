// Services/ExportService.swift
// Echo Copilot — Exports journal entries and setups to shareable files.
// JSON preserves all fields; CSV opens cleanly in Excel / Google Sheets.

import Foundation

enum ExportService {

    // MARK: - Journal

    /// Exports all journal entries as a pretty-printed JSON file.
    static func journalJSON(_ entries: [JournalEntry]) throws -> URL {
        let encoder = JSONEncoder()
        encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
        encoder.dateEncodingStrategy = .iso8601
        let data = try encoder.encode(entries)
        return try write(data: data, filename: "echo-journal-\(today).json")
    }

    /// Exports journal entries as a CSV file for spreadsheet analysis.
    static func journalCSV(_ entries: [JournalEntry]) throws -> URL {
        var rows: [String] = [
            "Ticker,Entry Date,Exit Date,Entry Price,Exit Price,Stop Price," +
            "Target 1,Target 2,P&L ($),R-Multiple,Tags,Notes"
        ]
        let df = DateFormatter()
        df.dateStyle = .short
        df.timeStyle = .none

        for e in entries {
            let row: [String] = [
                e.ticker,
                df.string(from: e.entryDate),
                e.exitDate.map { df.string(from: $0) } ?? "",
                String(format: "%.4f", e.entryPrice),
                e.exitPrice.map    { String(format: "%.4f", $0) } ?? "",
                e.stopPrice.map    { String(format: "%.4f", $0) } ?? "",
                e.target1.map      { String(format: "%.4f", $0) } ?? "",
                e.target2.map      { String(format: "%.4f", $0) } ?? "",
                e.pnlDollars.map   { String(format: "%.2f",  $0) } ?? "",
                e.pnlR.map         { String(format: "%.3f",  $0) } ?? "",
                csvQuote(e.tags.joined(separator: "; ")),
                csvQuote(e.notes)
            ]
            rows.append(row.joined(separator: ","))
        }

        let csv = rows.joined(separator: "\n")
        guard let data = csv.data(using: .utf8) else {
            throw ExportError.encodingFailed
        }
        return try write(data: data, filename: "echo-journal-\(today).csv")
    }

    // MARK: - Setups

    /// Exports all setups as a pretty-printed JSON file (for backup / import).
    static func setupsJSON(_ setups: [TickerSetup]) throws -> URL {
        let encoder = JSONEncoder()
        encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
        encoder.dateEncodingStrategy = .iso8601
        let data = try encoder.encode(setups)
        return try write(data: data, filename: "echo-setups-\(today).json")
    }

    // MARK: - Helpers

    private static var today: String {
        let df = DateFormatter()
        df.dateFormat = "yyyy-MM-dd"
        return df.string(from: Date())
    }

    private static func csvQuote(_ s: String) -> String {
        let escaped = s.replacingOccurrences(of: "\"", with: "\"\"")
        return "\"\(escaped)\""
    }

    private static func write(data: Data, filename: String) throws -> URL {
        let url = FileManager.default.temporaryDirectory.appendingPathComponent(filename)
        try data.write(to: url, options: .atomic)
        return url
    }

    enum ExportError: LocalizedError {
        case encodingFailed
        var errorDescription: String? { "Failed to encode export data." }
    }
}
