<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [`tools/mail-source/`](#toolsmail-source)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/licenses/LICENSE-2.0 -->

# `tools/mail-source/`

**Capability:** capability:setup + capability:intake

Mail-source backend abstraction. Pluggable backends (mbox, IMAP, future Mailman 3 / Hyperkitty) that feed the security-issue-import intake pipeline a uniform thread/message view. See [`contract.md`](contract.md) for the backend interface.
