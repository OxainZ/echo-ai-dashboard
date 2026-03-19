// Services/ClipboardService.swift
// Echo Copilot — Clipboard abstraction

import UIKit

// MARK: - Protocol

protocol ClipboardServiceProtocol {
    func copy(_ text: String)
}

// MARK: - Live implementation

final class LiveClipboardService: ClipboardServiceProtocol {
    func copy(_ text: String) {
        UIPasteboard.general.string = text
    }
}
