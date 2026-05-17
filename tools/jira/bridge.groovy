// SPDX-License-Identifier: Apache-2.0
// https://www.apache.org/licenses/LICENSE-2.0

@Grab('org.apache.groovy:groovy-json:4.0.21')
import groovy.json.JsonOutput
import groovy.json.JsonSlurper

/**
 * Read-only JIRA REST bridge for the issue-* skill family.
 *
 * Subcommands:
 *   search <JQL>          run a JQL query, emit matching issues as JSON
 *   issue <KEY>           fetch a single issue's full state as JSON
 *   projects              list the JIRA projects at the configured tracker URL
 *
 * Configuration (environment only; the caller — typically a skill —
 * resolves these from <project-config>/issue-tracker-config.md and
 * exports them. The bridge does NOT read that file itself):
 *   ISSUE_TRACKER_URL       e.g. https://issues.apache.org/jira
 *   ISSUE_TRACKER_PROJECT   the project key (e.g. FOO)
 *   JIRA_API_TOKEN          optional; base64-encoded "email:token" for authenticated reads
 *
 * Output: JSON to stdout. Errors: non-zero exit + message to stderr.
 *
 * Read-only by design: never performs POST, PATCH, or DELETE requests. Mutations
 * belong to the skill apply phases with explicit user confirmation.
 */

def ENV = System.getenv()
def TRACKER_URL = ENV['ISSUE_TRACKER_URL'] ?: ''
def PROJECT_KEY = ENV['ISSUE_TRACKER_PROJECT'] ?: ''
def API_TOKEN   = ENV['JIRA_API_TOKEN'] ?: ''

if (!TRACKER_URL) {
    System.err.println('error: ISSUE_TRACKER_URL not set in the environment (the calling skill resolves it from <project-config>/issue-tracker-config.md and exports it)')
    System.exit(2)
}

def httpGet(String urlStr) {
    def url = new URL(urlStr)
    def conn = url.openConnection()
    conn.requestMethod = 'GET'
    conn.setRequestProperty('Accept', 'application/json')
    if (API_TOKEN) {
        conn.setRequestProperty('Authorization', "Basic ${API_TOKEN}")
    }
    conn.connectTimeout = 10000
    conn.readTimeout    = 30000
    def code = conn.responseCode
    if (code < 200 || code >= 300) {
        def err = conn.errorStream ? conn.errorStream.text : conn.responseMessage
        System.err.println("error: HTTP ${code} fetching ${urlStr}\n${err}")
        System.exit(3)
    }
    return new JsonSlurper().parse(conn.inputStream)
}

def emit(Object payload) {
    println JsonOutput.prettyPrint(JsonOutput.toJson(payload))
}

def shape_issue(Map raw) {
    [
        key:          raw.key,
        title:        raw.fields?.summary,
        status:       raw.fields?.status?.name,
        resolution:   raw.fields?.resolution?.name,
        components:   raw.fields?.components?.collect { it.name } ?: [],
        fixVersions:  raw.fields?.fixVersions?.collect { it.name } ?: [],
        priority:     raw.fields?.priority?.name,
        reporter:     raw.fields?.reporter?.displayName,
        assignee:     raw.fields?.assignee?.displayName,
        created:      raw.fields?.created,
        updated:      raw.fields?.updated,
        description:  raw.fields?.description,
        comments:     raw.fields?.comment?.comments?.collect {
            [author: it.author?.displayName, body: it.body, created: it.created]
        } ?: [],
        url:          "${TRACKER_URL}/browse/${raw.key}",
    ]
}

def cmd_search(List args) {
    def jql = args ? args[0] : null
    def limit = 50
    def i = 1
    while (i < args.size()) {
        if (args[i] == '--limit' && i + 1 < args.size()) {
            limit = args[i + 1].toInteger()
            i += 2
        } else {
            i++
        }
    }
    if (!jql) {
        System.err.println('error: search requires a JQL string')
        System.exit(2)
    }
    def encoded = URLEncoder.encode(jql, 'UTF-8')
    def url = "${TRACKER_URL}/rest/api/2/search?jql=${encoded}&maxResults=${limit}&fields=summary,status,resolution,components,fixVersions,priority"
    def result = httpGet(url)
    emit([
        total: result.total,
        returned: result.issues?.size() ?: 0,
        issues: (result.issues ?: []).collect { shape_issue(it) },
    ])
}

def cmd_issue(List args) {
    def key = args ? args[0] : null
    if (!key) {
        System.err.println('error: issue requires a tracker key (e.g. FOO-9999)')
        System.exit(2)
    }
    if (!(key ==~ /^[A-Z][A-Z0-9_]*-\d+$/)) {
        System.err.println("error: '${key}' is not a valid tracker key")
        System.exit(2)
    }
    def url = "${TRACKER_URL}/rest/api/2/issue/${key}?fields=*all"
    def result = httpGet(url)
    emit(shape_issue(result))
}

def cmd_projects(List args) {
    def url = "${TRACKER_URL}/rest/api/2/project"
    def result = httpGet(url)
    emit([
        count: result.size(),
        projects: result.collect { [key: it.key, name: it.name, id: it.id] },
    ])
}

def args = this.args as List
if (!args) {
    System.err.println('usage: groovy bridge.groovy <search|issue|projects> [args]')
    System.exit(2)
}

def subcmd = args[0]
def rest   = args.size() > 1 ? args[1..-1] : []

switch (subcmd) {
    case 'search':   cmd_search(rest);   break
    case 'issue':    cmd_issue(rest);    break
    case 'projects': cmd_projects(rest); break
    default:
        System.err.println("error: unknown subcommand '${subcmd}' (expected: search, issue, projects)")
        System.exit(2)
}
