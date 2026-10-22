# Licensing and redistribution

**Invoke, do not vendor.** The MIT [LICENSE](../LICENSE) applies to original scripts, skills, documentation, tests and configuration. It does not relicense external tools/data, dependencies, Blizzard assets, or trademarks.

No external executable, GPL source, API database, external language-server schema, simulator, Lua framework, or runtime agent addon is distributed. Integration uses original instructions, path detection, and invocation of independently installed software. The packaged MCP configuration lets the host start an original Node launcher, which resolves and starts an existing server. The launcher and configuration use this project's MIT license; no server implementation, runtime, dependency, API dataset, or wiki cache is included. Declaring the connection does not grant rights to redistribute upstream material.

Before copying or releasing material:

- Identify exact repository, version/revision, license text and separate notices. A package license field alone is not a complete provenance review.
- Keep upstream source, binaries, tool-managed caches, and restricted data outside this repository and ZIPs. Do not copy unknown-provenance snippets into generated addons.
- GPL tools stay separate executables. No GPL source/binary is redistributed, linked into these Python helpers, or translated into the project.
- Lychee stays user-installed regardless of its current project code license. Its notices identify unresolved image provenance and dependency terms; do not relicense its bundle as MIT.
- BigWigs externals/localizations and MCP source/wiki caches are separate downloads. Invoking a tool does not authorize fetching, copying, relicensing, or shipping those materials.
- Preserve attribution/share-alike obligations for separately authorized derived content. Warcraft Wiki content is not bundled here.
- Maintain [third-party notices](../THIRD_PARTY_NOTICES.md) when identities or licenses change. Record uncertainty rather than asserting an unverified license grant.

## Artwork and marks

[The logo](../assets/README.md) was supplied for this project and is included unchanged. The original-code MIT grant excludes that artwork and third-party trademarks. The owner supplied the generated artwork for this identity. This provenance note records its separate scope; it is not a detected licensing defect.

World of Warcraft/Blizzard, OpenAI/Codex, and Anthropic/Claude identify interoperability targets. No affiliation, endorsement, or trademark rights are claimed.

## Release boundary

Run tests and validation; build separate host ZIPs; inspect archive contents, hashes, notices and versions. Packaging uses an allowlist and omits the other host's metadata, secrets, caches and developer tooling. An archive on disk is not evidence of installation, directory approval, publication, or in-game testing.
