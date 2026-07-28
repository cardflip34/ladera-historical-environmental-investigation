#!/usr/bin/env swift
import AppKit
import Foundation
import Vision

// OCR rendered PDF page images with macOS Vision.
// Usage: swift scripts/ocr_pdf_vision.swift <image-directory> <output.txt>

guard CommandLine.arguments.count == 3 else {
    FileHandle.standardError.write(
        Data("Usage: ocr_pdf_vision.swift <image-directory> <output.txt>\n".utf8)
    )
    exit(2)
}

let imageDirectory = URL(fileURLWithPath: CommandLine.arguments[1], isDirectory: true)
let outputURL = URL(fileURLWithPath: CommandLine.arguments[2])
let manager = FileManager.default

let files = try manager.contentsOfDirectory(
    at: imageDirectory,
    includingPropertiesForKeys: nil,
    options: [.skipsHiddenFiles]
).filter { ["png", "jpg", "jpeg"].contains($0.pathExtension.lowercased()) }
 .sorted { $0.lastPathComponent.localizedStandardCompare($1.lastPathComponent) == .orderedAscending }

var output = ""
for (index, file) in files.enumerated() {
    guard let image = NSImage(contentsOf: file) else {
        FileHandle.standardError.write(Data("Skipping unreadable image: \(file.path)\n".utf8))
        continue
    }
    var rect = NSRect(origin: .zero, size: image.size)
    guard let cgImage = image.cgImage(forProposedRect: &rect, context: nil, hints: nil) else {
        FileHandle.standardError.write(Data("Skipping image without CGImage: \(file.path)\n".utf8))
        continue
    }

    let request = VNRecognizeTextRequest()
    request.recognitionLevel = .accurate
    request.usesLanguageCorrection = true
    request.recognitionLanguages = ["en-US"]
    let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])
    try handler.perform([request])

    let observations = (request.results ?? []).sorted { left, right in
        let yDifference = left.boundingBox.midY - right.boundingBox.midY
        if abs(yDifference) > 0.015 { return yDifference > 0 }
        return left.boundingBox.minX < right.boundingBox.minX
    }
    output += "\n=== PAGE \(index + 1): \(file.lastPathComponent) ===\n"
    for observation in observations {
        if let candidate = observation.topCandidates(1).first {
            output += candidate.string + "\n"
        }
    }
    print("OCR \(index + 1)/\(files.count): \(file.lastPathComponent)")
}

try output.write(to: outputURL, atomically: true, encoding: .utf8)
