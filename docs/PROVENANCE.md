# License and source provenance

This release is published by avalonreset under the MIT license in LICENSE.
The project owner authorized releasing the original local kit as open source.
The public Python transport and operation registry were adapted from that
project; portable CLI, documentation, examples, and release checks accompany it.
The earlier local package was marked private/proprietary. That label described
the unreleased local distribution; this public release has the owner's MIT
grant. No private distribution archive or private repository history is included.

No third-party SDK implementation, vendor example source, or MCP server source
is bundled. Runtime code uses the Python standard library. Build/test tools are
installed as development dependencies under their own licenses and are not
vendored. Synthetic test fixtures are authored for this project, not captured
customer or account responses.

Endpoint paths and field contracts were checked against the provider's public
documentation on 2026-09-20:

- [Authentication](https://docs.dataforseo.com/v3/auth/)
- [Maps task POST](https://docs.dataforseo.com/v3/serp/google/maps/task_post/)
- [Maps task GET advanced](https://docs.dataforseo.com/v3/serp/google/maps/task_get/advanced/)
- [Keyword overview](https://docs.dataforseo.com/v3/dataforseo_labs/google/keyword_overview/live/)
- [Pricing](https://dataforseo.com/pricing)

Documentation informs interoperability; it is not copied into this package.
The MIT grant covers this project's code and documentation. DataForSEO service
access, returned data, pricing, and trademarks remain governed by their owners.
