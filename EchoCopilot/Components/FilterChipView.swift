// Components/FilterChipView.swift
// Echo Copilot — Tappable filter chip with selected/unselected state

import SwiftUI

struct FilterChipView: View {
    let title: String
    let isSelected: Bool
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            Text(title)
                .font(.system(size: 13, weight: isSelected ? .semibold : .regular))
                .foregroundStyle(isSelected ? .black : .primary)
                .padding(.horizontal, 12)
                .padding(.vertical, 6)
                .background(isSelected ? Color.accentColor : Color(.systemGray5), in: Capsule())
        }
        .buttonStyle(.plain)
    }
}

#Preview {
    HStack {
        FilterChipView(title: "All", isSelected: true, action: {})
        FilterChipView(title: "Actionable", isSelected: false, action: {})
        FilterChipView(title: "Shadow", isSelected: false, action: {})
    }
    .padding()
    .background(.black)
}
