// Utilities/ClipboardHelper.swift
// Echo Copilot — UIPasteboard wrapper

import UIKit

enum ClipboardHelper {
    static func copy(_ text: String) {
        UIPasteboard.general.string = text
    }

    static func paste() -> String? {
        UIPasteboard.general.string
    }
}
