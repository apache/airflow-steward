// SPDX-License-Identifier: Apache-2.0
// https://www.apache.org/licenses/LICENSE-2.0

import groovy.json.JsonSlurper
import groovy.xml.MarkupBuilder
// groovy.json and groovy.xml are bundled with the Groovy distribution
// since 3.0; no @Grab required.

/**
 * Deterministic reference implementation of the issue-reassess-stats
 * dashboard. Reads verdict.json files from a campaign directory,
 * computes aggregates per issue-reassess-stats/aggregate.md, and emits
 * the HTML per issue-reassess-stats/render.md.
 *
 * Invocation:
 *   groovy reference.groovy <campaign-dir> [--output <file>]
 */

def args = this.args as List
if (args.size() < 1) {
    System.err.println('usage: groovy reference.groovy <campaign-dir> [--output <file>]')
    System.exit(2)
}

def campaignDir = new File(args[0])
if (!campaignDir.exists() || !campaignDir.isDirectory()) {
    System.err.println("error: not a directory: ${campaignDir}")
    System.exit(2)
}

def outputFile = null
def i = 1
while (i < args.size()) {
    if (args[i] == '--output' && i + 1 < args.size()) {
        outputFile = new File(args[i + 1])
        i += 2
    } else { i++ }
}

// --- Step 1: Fetch ---
def slurper = new JsonSlurper()
def verdicts = []
def parseErrors = []
campaignDir.eachFile { entry ->
    if (entry.isDirectory()) {
        def vf = new File(entry, 'verdict.json')
        if (vf.exists()) {
            try {
                verdicts << slurper.parse(vf)
            } catch (Throwable t) {
                parseErrors << [path: vf.path, error: t.message]
            }
        }
    }
}

if (verdicts.isEmpty()) {
    System.err.println("error: no verdict.json files found under ${campaignDir}")
    System.exit(2)
}

// --- Step 2: Classify ---
def classifyBuckets = [
    'fixed':              ['fixed-on-master'],
    'still-failing':      ['still-fails-same', 'still-fails-different'],
    'closed-as-intended': ['intended-behaviour'],
    'closed-as-duplicate':['duplicate-of-resolved'],
    'unrun':              ['cannot-run-extraction', 'cannot-run-environment',
                           'cannot-run-dependency', 'timeout', 'needs-separate-workspace'],
]
def bucketOf = { String c -> classifyBuckets.find { k, vs -> c in vs }?.key ?: 'unknown' }

def total = verdicts.size()
// 'unknown' is included so a verdict whose classification isn't in
// any bucket increments a real 0 rather than null++ (which throws).
def buckets = (classifyBuckets.keySet() + 'unknown').collectEntries { [(it): 0] }
verdicts.each { v -> buckets[bucketOf(v.classification)]++ }

def partialFix = verdicts.findAll { v ->
    v.cases instanceof List && v.cases.any { it.match_on_master == true } && v.cases.any { it.match_on_master == false }
}
def newIssueCandidates = []
verdicts.each { v ->
    def f1 = v.cross_type_probe?.findings
    def f2 = v.operator_variants_probe?.findings
    if (f1) newIssueCandidates << [key: v.key, family: 'cross-type', findings: f1]
    if (f2) newIssueCandidates << [key: v.key, family: 'operator-variants', findings: f2]
}

// --- Step 3: Aggregate ---
def stillFailing = buckets['still-failing'] ?: 0
def unrun = buckets['unrun'] ?: 0
def stillFailingPct = total > 0 ? (stillFailing * 100.0 / total) : 0
def unrunPct = total > 0 ? (unrun * 100.0 / total) : 0

def rating
if (stillFailingPct < 5 && unrunPct < 20) rating = 'Healthy'
else if (stillFailingPct < 20 && unrunPct < 40) rating = 'Needs attention'
else rating = 'Action needed'

def heroColor = { String card ->
    if (card == 'still-failing') return stillFailingPct > 20 ? 'red' : stillFailingPct > 5 ? 'amber' : 'green'
    if (card == 'fixed') return 'green'
    if (card == 'partial-fix') return partialFix.size() > 0 ? 'amber' : 'green'
    if (card == 'unrun') return unrunPct > 50 ? 'red' : unrunPct > 30 ? 'amber' : 'green'
    return 'neutral'
}

def actionCandidates = verdicts.findAll {
    it.classification in ['still-fails-same', 'still-fails-different'] &&
    it.nature == 'bug-as-advertised'
}.sort { it.key }

def closureCandidates = verdicts.findAll {
    it.classification == 'fixed-on-master' && it.nature == 'bug-as-advertised'
}.sort { it.key }

def trackerHygiene = verdicts.findAll {
    it.nature == 'feature-request-disguised-as-bug'
}.sort { it.key }

// --- Step 4: Render ---
def sw = new StringWriter()
def mb = new MarkupBuilder(sw)
mb.html {
    head {
        meta(charset: 'UTF-8')
        title("Reassessment dashboard — ${campaignDir.name}")
        style('''
            body { font-family: -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; max-width: 1100px; margin: 24px auto; padding: 0 16px; background:#fff; color:#1f2328; }
            h1, h2 { border-bottom: 1px solid #d0d7de; padding-bottom: 6px; }
            .hero { display: flex; gap: 12px; margin: 16px 0; }
            .card { flex: 1; padding: 16px; border-radius: 8px; background: #f6f8fa; }
            .card.red    { background: #ffe9e6; }
            .card.amber  { background: #fff8c5; }
            .card.green  { background: #dafbe1; }
            .card .label { font-size: 11px; color: #57606a; text-transform: uppercase; }
            .card .value { font-size: 28px; font-weight: 600; }
            .rating { padding: 12px 16px; border-radius: 8px; margin: 12px 0; font-weight: 600; }
            .rating.red   { background: #cf222e; color: #fff; }
            .rating.amber { background: #bf8700; color: #fff; }
            .rating.green { background: #2da44e; color: #fff; }
            table { width: 100%; border-collapse: collapse; margin: 12px 0; }
            th, td { padding: 6px 8px; text-align: left; border-bottom: 1px solid #d0d7de; font-size: 13px; }
            tr:nth-child(even) { background: #f6f8fa; }
            details summary { cursor: pointer; padding: 8px 0; }
            .footer { font-size: 12px; color: #57606a; margin-top: 24px; padding-top: 12px; border-top: 1px solid #d0d7de; }
            @media (prefers-color-scheme: dark) {
                body { background: #0d1117; color: #e6edf3; }
                .card { background: #161b22; }
                .footer { color: #8b949e; }
            }
        ''')
    }
    body {
        h1("Reassessment dashboard — ${campaignDir.name}")

        div(class: 'hero') {
            [
                ['Candidates',         total,             'neutral'],
                ['Still failing',      stillFailing,      heroColor('still-failing')],
                ['Fixed on master',    buckets['fixed'],  heroColor('fixed')],
                ['Partial fix',        partialFix.size(), heroColor('partial-fix')],
                ['Unrun',              unrun,             heroColor('unrun')],
            ].each { label, val, color ->
                div(class: "card ${color}") {
                    div(class: 'label', label)
                    div(class: 'value', String.valueOf(val))
                }
            }
        }

        div(class: "rating ${rating == 'Healthy' ? 'green' : rating == 'Action needed' ? 'red' : 'amber'}",
            "Health: ${rating}")

        h2('Action candidates')
        if (actionCandidates) {
            ol {
                actionCandidates.each { v ->
                    li {
                        b(v.key)
                        mkp.yield(' — ')
                        span("classification=${v.classification}; nature=${v.nature}")
                        br()
                        small("Next: /issue-fix-workflow ${v.key}")
                    }
                }
            }
        } else {
            p('No still-failing × bug-as-advertised candidates in this campaign.')
        }

        h2('Closure candidates')
        if (closureCandidates) {
            ul {
                closureCandidates.each { v ->
                    li("${v.key} — fixed-on-master (${v.rev}); confirm and close")
                }
            }
        } else {
            p('No fixed-on-master × bug-as-advertised candidates.')
        }

        h2('New-issue candidates')
        if (newIssueCandidates) {
            ul {
                newIssueCandidates.each { c ->
                    li("${c.key} (${c.family}): ${c.findings}")
                }
            }
        } else {
            p('No probes surfaced new-issue candidates.')
        }

        h2('Tracker hygiene')
        if (trackerHygiene) {
            ul {
                trackerHygiene.each { v ->
                    li("${v.key} — re-type as Improvement (feature-request-disguised-as-bug)")
                }
            }
        } else {
            p('No feature-request-disguised-as-bug verdicts.')
        }

        details {
            summary('Per-issue table (collapsible)')
            table {
                thead {
                    tr { ['Key','Class','Nature','Shape','Rev'].each { th(it) } }
                }
                tbody {
                    verdicts.sort { it.key }.each { v ->
                        tr {
                            td(v.key)
                            td(v.classification)
                            td(v.nature)
                            td(v.shape)
                            td(v.rev)
                        }
                    }
                }
            }
        }

        div(class: 'footer') {
            p("Campaign: ${campaignDir.name}")
            p("Candidates: ${total} | Parse errors: ${parseErrors.size()}")
            if (parseErrors) {
                ul {
                    parseErrors.each { e -> li("${e.path}: ${e.error}") }
                }
            }
        }
    }
}

def html = sw.toString()
if (outputFile) {
    outputFile.text = html
    System.err.println("wrote ${outputFile.path} (${html.size()} bytes)")
} else {
    println html
}
