# anima

Anima is a database product built on a fork of PostgreSQL. Existing
products fill the capabilities PostgreSQL lacks, each behind a standard
contract so that it stays replaceable; the first is authentication against an
OpenID Connect identity provider. What Anima adds is their integration:
configured to work together out of the box, specified, tested and released as
one thing.

The **engine** is the runtime Anima ships: the database server built from the
PostgreSQL fork, together with every adapter and the wiring that makes them
work together. Your **configuration** (the identities and the installation
parameters) lives outside the engine, in a directory you mount into it, and you
never edit the engine.

The engine is delivered as one **engine image**, decided and not yet built. It
is meant to start in two ways: booted as the operating system of a machine, or
run as a container by a container engine that needs no daemon and no root. You
are never asked to install or manage an orchestrator, and Docker is not used.

Copyright (C) 2026 Cocreiamo di Bilotta Francesco

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, version 3 of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

The full text of the license is in [LICENSE](LICENSE).

## Licensing

- **Anima and its official plugins** are licensed under the GNU Affero
  General Public License, version 3. The core will always remain available
  under this license.
- **Your plugins, configuration and data** are yours. The
  [Anima Plugin Exception](PLUGIN-EXCEPTION.md) lets you license plugins
  and generated code under terms of your choice. Changes to Anima itself
  remain under the AGPL.
- **Commercial licenses** are available from Cocreiamo for those who
  cannot meet the terms of the AGPL: write to licensing@cocreiamo.com.

## Contributing

Contributions are accepted only under the
[Contributor License Agreement](CLA.md). The agreement lets Cocreiamo offer
commercial licenses as well as the AGPL. Signing records some personal data:
see the [privacy notice](PRIVACY.md).

## Trademarks

COCREIAMO and ANIMA are trademarks of Cocreiamo di Bilotta Francesco. The
open source license does not grant rights to use them: see the
[Trademark Policy](TRADEMARKS.md).
