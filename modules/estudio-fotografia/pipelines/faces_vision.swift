// Detecção de rostos com o Vision do macOS (nativo, sem download).
// uso: swift faces_vision.swift img1.jpg img2.jpg ...  → por linha: caminho \t x,y,w,h;x,y,w,h (frações, origem topo-esquerda)
import Foundation
import Vision
import AppKit

for path in CommandLine.arguments.dropFirst() {
    guard let img = NSImage(contentsOfFile: path),
          let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
        print("\(path)\tERR"); continue
    }
    let req = VNDetectFaceRectanglesRequest()
    let handler = VNImageRequestHandler(cgImage: cg, options: [:])
    do { try handler.perform([req]) } catch { print("\(path)\tERR"); continue }
    var out: [String] = []
    for f in req.results ?? [] {
        let b = f.boundingBox
        out.append(String(format: "%.4f,%.4f,%.4f,%.4f", b.origin.x, 1 - b.origin.y - b.size.height, b.size.width, b.size.height))
    }
    print("\(path)\t" + out.joined(separator: ";"))
}
