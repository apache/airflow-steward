<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [`tools/apache-projects/`](#toolsapache-projects)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/licenses/LICENSE-2.0 -->

# `tools/apache-projects/`

**Capability:** capability:stats + capability:intake

ASF project-metadata substrate. Read-only, unauthenticated client
for the official `apache/comdev` `apache-projects-mcp` server, which
wraps the public `projects.apache.org/json` feeds (committee /
committer rosters, people + Apache IDs, podlings, releases, LDAP
groups, repositories). Used by `contributor-nomination` (Apache ID
verification, vendor-neutrality / employer context) and the
roster-resolution paths in the security skills. For ASF projects it
is a mandatory pre-flight prerequisite, installed from the latest
`main` of `apache/comdev`. See [`tool.md`](tool.md) for the
operation catalogue, setup, and the track-`main` install contract.
