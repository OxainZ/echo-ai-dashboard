// Utilities/Formatters.swift
// Echo Copilot — Centralized number, percent, and date formatting

import Foundation

// MARK: - Double formatting

extension Double {
    /// Currency format: $47.32
    var asCurrency: String {
        let f = NumberFormatter()
        f.numberStyle = .currency
        f.currencySymbol = "$"
        f.minimumFractionDigits = 2
        f.maximumFractionDigits = 2
        return f.string(from: NSNumber(value: self)) ?? "$\(self)"
    }

    /// Price with 2 decimal places: 47.32
    var asPrice: String {
        String(format: "%.2f", self)
    }

    /// Percent with 2 decimal places: 0.35%
    var asPercent: String {
        String(format: "%.2f%%", self)
    }

    /// Multiplier format: 2.4x
    var asMultiplier: String {
        String(format: "%.1fx", self)
    }

    /// Rounded to 2 decimal places: 1.82
    var rounded2: String {
        String(format: "%.2f", self)
    }

    /// Large dollar volumes: $1.2M, $340K
    var asShortDollar: String {
        switch abs(self) {
        case 1_000_000_000...:
            return String(format: "$%.1fB", self / 1_000_000_000)
        case 1_000_000...:
            return String(format: "$%.1fM", self / 1_000_000)
        case 1_000...:
            return String(format: "$%.0fK", self / 1_000)
        default:
            return String(format: "$%.0f", self)
        }
    }
}

// MARK: - Optional Double formatting

extension Optional where Wrapped == Double {
    var asCurrencyOrNA: String { self?.asCurrency ?? "N/A" }
    var asPriceOrNA: String { self?.asPrice ?? "N/A" }
    var asPercentOrNA: String { self?.asPercent ?? "N/A" }
    var asMultiplierOrNA: String { self?.asMultiplier ?? "N/A" }
    var asRounded2OrNA: String { self?.rounded2 ?? "N/A" }
    var asShortDollarOrNA: String { self?.asShortDollar ?? "N/A" }
}

// MARK: - Date formatting

extension Date {
    var asTimeString: String {
        let f = DateFormatter()
        f.dateFormat = "h:mm a"
        return f.string(from: self)
    }

    var asDateString: String {
        let f = DateFormatter()
        f.dateStyle = .medium
        f.timeStyle = .none
        return f.string(from: self)
    }

    var asDateTimeString: String {
        let f = DateFormatter()
        f.dateStyle = .short
        f.timeStyle = .short
        return f.string(from: self)
    }
}
