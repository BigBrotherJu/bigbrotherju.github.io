# Web Automation Basics

## Resources

- Knowledge base associated with web scraping reddit

  https://webscraping.fyi/

- https://scrapfly.io/academy

- https://docs.apify.com/academy

## Browser Automation

https://webscraping.fyi/overview/browser-automation/

https://github.com/angrykoala/awesome-browser-automation

- HTTP clients and browser automation tools

  - HTTP clients

    Cannot execute javascript.

    - `httpx` in Python
    - `requests` in Python
    - `axios` in Python

  - Browser automation libraries

    - Playwright
    - Puppeteer
    - Selenium

## Web Scraping Bot Detection/Blocking

https://scrapfly.io/academy/scraper-blocking

https://scrapfly.io/blog/posts/how-to-scrape-without-getting-blocked-tutorial/

https://scrapfly.io/blog/posts/how-to-avoid-web-scraping-blocking-tls

https://scrapfly.io/blog/posts/how-to-avoid-web-scraping-blocking-javascript

https://docs.apify.com/academy/anti-scraping

https://docs.apify.com/academy/anti-scraping/techniques/fingerprinting

### HTTP Header

To scrape data from a web page without getting detected, we have to carefully configure headers:

- Ensure the HTTP request header matches a real browser.

- Aim for the common header values of a major browser, such as Chrome on Windows or Safari on MacOS.

- Randomize the header values when scraping at scale, such as **User-Agent** rotation.

- Ensure the header order matches the regular browser and your HTTP client respects the header order.

- Cookie header

  Usually, cookie values contain localization, authorization, and user details.

  Correctly adding these values can help avoid detection, especially when scraping hidden APIs.

- HTTP2

#### User Agent 和浏览器版本

- Chrome 版本

  https://chromiumdash.appspot.com/releases?platform=Windows

  chrome 都是自动升级的，正常用户没有人会用一个老版本的 chrome。

  Security systems know that the only people who disable auto-updates are:

  - Corporate IT environments (managed devices).
  - Malware victims.
  - Botters/Scrapers using old software.

- Chrome 的 user agent

  考虑到谷歌的 User-Agent Reduction，chrome ua 的成分如下：

  - `Mozilla/5.0` 冻结，历史原因
  - `(...)` 部分冻结，macOS 永远显示 Mac OS X 10_15_7，windows 永远显示 Windows NT 10.0
  - `AppleWebKit/537.36` 冻结，历史原因
  - `(KHTML, like Gecko)` 冻结，历史原因
  - `Chrome/141.0.0.0` 部分冻结，只有大版本会变动，小版本都是 0
  - `Safari/537.36` 冻结，历史原因

  ```
  Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36
  ```

- `Sec-CH-UA`

  真正的信息在 `Sec-CH-UA-` 里。

  一般这三个会在每一次 request 里。

  ```
  sec-ch-ua
  "Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"
  sec-ch-ua-mobile
  ?0
  sec-ch-ua-platform
  "macOS"
  ```

  下面这三个只有在服务器问的情况下才会发给服务器：

  ```
  Sec-CH-UA-Full-Version-List (Exact minor version, e.g., 125.0.6422.60)
  Sec-CH-UA-Model (e.g., "Pixel 7")
  Sec-CH-UA-Arch (e.g., "x86")
  ```

### IP Address

#### IP and ASN

- IP address allocation hierarchy

  - IANA

    At the very top is the IANA (Internet Assigned Numbers Authority), which is a part of ICANN. Think of IANA as the "manufacturer" that creates and holds the entire global pool of IP addresses.

  - The 5 RIRs

    IANA does not deal with individual ISPs. Instead, it distributes massive blocks of IPs to five RIRs (Regional Internet Registries).

    Each RIR is a non-profit organization that manages all the IPs for its specific geographic region of the world.

    The five RIRs are:

    - ARIN: North America
    - RIPE NCC: Europe, the Middle East, and Central Asia
    - APNIC: Asia-Pacific
    - LACNIC: Latin America and the Caribbean
    - AFRINIC: Africa

  - LIRs / End-user

    The RIRs then allocate or assign smaller blocks of IPs to organizations within their region.

    The RIRs have two main "customer" types: LIRs and end-users.

    LIRs (Local Internet Registries) get large "Provider-Aggregatable" (PA) block **allocation** of IPs to distribute from RIR, and assign IPs to their customers for profit. (IANA -> RIR -> LIR -> customer)

    End-users get a "Provider-Independent" (PI) block **assignment** of IPs for portability from RIR, and use IPs for their own internal network. (IANA -> RIR -> End-User)

    LIRs can be:

    - Internet Service Providers (Home internet)

      Verizon, Comcast, AT&T, 中国电信

    - Telecommunication companies (Mobile network)

      T-Mobile, Verizon Wireless, AT&T Mobility

    - Cloud & hosting providers

      Amazon Web Services (AWS), Google Cloud, Microsoft Azure, DigitalOcean, OVH

      Their entire business is renting servers (which need IPs) to customers.

    End-users can be:

    - Corporations

      Large corporations like Ford need many IPs for their internal network.

    - Universities

    - Government agencies

      A nation's Department of Defense, a national research lab, or large federal agencies.

    - Non-profit org

      Large research consortiums or foundational organizations.

- ASN allocation hierarchy

  - IANA to RIRs (The Global Pool)

    Who: IANA (Internet Assigned Numbers Authority)

    To Whom: The five RIRs (Regional Internet Registries: ARIN, RIPE, APNIC, LACNIC, AFRINIC)

    IANA manages the central, global pool of all available ASNs. It doesn't deal with individual companies; it allocates large blocks of ASNs to each of the five RIRs to manage for their specific geographic region.

  - RIRs to Organizations (The Final Assignment)

    Who: The RIRs (like ARIN, RIPE, etc.)

    To Whom: Any organization that can demonstrate the technical need to run its own independent network.

    This is the main "assignment" step. The RIRs are the ones who give ASNs to "end-users" (in the broad sense).

    These organizations include:

    - ISPs (Internet Service Providers)
    - Telecommunication Companies (mobile carriers)
    - Cloud & Hosting Providers (like AWS, Google Cloud, DigitalOcean)
    - Large Corporations (like Google, Microsoft, Ford)
    - Universities
    - Government Agencies

    These organizations need an ASN so they can control their own network routing using BGP (Border Gateway Protocol) and announce their IP address blocks to the rest of the internet.

- Whole process

  - Get IPs from RIR

    An LIR (like Comcast) or a large End-User (like a university) applies to their RIR (like ARIN) and gets a block of IP addresses. This is the "resource" they own.

  - Get ASN from RIR

    Because they want to control their own routing for those IPs (e.g., for redundancy or portability), they also apply to the RIR for an Autonomous System Number (ASN). This is their "network ID."

  - Use BGP to Announce

    This is the key. They configure their network's "border routers" to use BGP (Border Gateway Protocol). This protocol sends out a constant, public announcement to their neighboring networks that says:

    "Hey, world! If you want to reach any IP in my block (192.0.2.0/24), send the traffic to me. I am ASN 64500."

    The other networks (ISPs) hear this announcement, add it to their global routing tables, and the "mapping" is complete. The rest of the internet now knows that ASN 64500 is the correct path to reach those IPs.

- Relationship between ASN and IP

  Every public IP address that is **active on the internet** is associated with an ASN.

  An IP address is just a "house number." The ASN is the "street" or "neighborhood" that the house is on.

  For a packet of data to find its way to an IP address, it must first be routed to the correct network (the "neighborhood"). The internet's routing system (BGP) works by telling all the other networks which "neighborhoods" (ASNs) it knows how to reach.

  If a public IP address isn't announced by an ASN, it's effectively "off the map." The rest of the internet has no way to find it or send traffic to it.

#### ipinfo

```
{
 ip:"104.234.157.142",
 city:"Jordan",
 region:"Yau Tsim Mong District",
 country:"HK",
 loc:"22.3054,114.1700",
 postal:"999077",
 timezone:"Asia/Hong_Kong",
 asn:{
  asn:"AS400618",
  name:"Prime Security Corp.",
  domain:"primesecuritycorp.com",
  route:"104.234.157.0/24",
  type:"hosting"
 },
 company:{
  name:"ONTAR-40 (Velcom INC)",
  domain:"velcom.com",
  type:"hosting"
 },
 privacy:{
  vpn:false,
  proxy:false,
  tor:false,
  relay:false,
  hosting:true,
  service:""
 },
 abuse:{
  address:"US, FL, Tampa, 8010 Woodland Center Blvd, Suite 700, 33614",
  country:"US",
  email:"abuse@hivelocity.net",
  name:"HIvelocity Network Abuse Administrator",
  network:"104.234.152.0/21",
  phone:"+1-888-869-4678"
 },
 domains:{
  page:0,
  total:0,
  domains:[]
 }
}
```

首先，在 ICANN 和 ARIN 上查 104.234.157.142，只能查到一家叫 Internet Utilities NA LLC 的公司。这个公司的 ip range 是 104.234.128.0/19。这只能说明 Internet Utilities 从 ARIN 那里获得了这些 ip，实际使用的人可能不是他们。

HIvelocity 和 Prime Security 这两家公司是怎么来的？是 ipinfo 通过查询公开的 BGP 信息获得的。Hivelocity (AS29802) 发送过 BGP 消息，说 104.234.152.0/21 是他们管的。Prime Security (AS400618) 也发送过 BGP 消息，说 104.234.157.0/24 是他们管的。

`company` 也是 ipinfo 自己分析出来的，ipinfo 通过某种方式知道 ONTAR-40 (Velcom INC) 是实际使用 104.234.157.142 这个 ip 的公司。

这个 ip 的层级关系是：Internet Utilities -> Hivelocity (AS29802) -> Prime Security Corp. (AS400618) → Velcom INC。

- Values for `type` field

  - `isp` (Internet Service Provider)
  - `hosting` (Data centers, cloud providers, and server hosts)
  - `business` (Corporate/enterprise networks)
  - `education` (Universities, schools, and research institutions)
  - `government` (Government agencies)

- IP reputation

  为了让您更清晰地理解，这里有一个IP类型的信誉（风险）排名：

  01. 最高信誉（风险最低）：asn.type = isp + company.type = isp
      - 含义: 住宅宽带 (Residential IP)。
      - 看起来像: 一个真实的家庭用户。
      - 就算 asn 和 company 不是一个公司，也没事。这是正常现象，asn 是 ip 批发商，company 从 asn 那里采购 ip，然后提供给住宅。
  02. 高信誉（风险很低）：asn.type = isp + company.type = business
      - 含义: 企业宽带（这就是您的情况）。
      - 看起来像: 一个真实的办公室员工。
  03. 可疑（有风险）：asn.type = isp + company.type = hosting
      - 含义: "双ISP" 或 "ISP代理" 的一种。数据中心（Hosting）租用了ISP的地址块。
      - 看起来像: 高级机器人。这种IP质量很高，但如果被滥用，也会被广告联盟盯上。
  04. 最低信誉（风险极高）：asn.type = hosting + company.type = hosting
      - 含义: 数据中心IP (Datacenter IP)。
      - 看起来像: 100% 的机器人（例如：来自亚马逊AWS、阿里云、Azure的服务器）。
      - 后果: 会被立即拦截或要求验证。

#### business ip 的问题

上面的信誉排名并不是广告商的视角。从广告商的视角出发，business ip 最好不要用。

第一，business 类型的 ip 可能实际上是 hosting。You are assuming "Business IP" means "IBM Headquarters." In the proxy world, "Business IP" usually means "Cheap VPS Hosting" or "School Library" or "Small Office."

Ad Tech Databases: Companies like MaxMind and Digital Element categorize IP ranges.

The Trap: Many "Business" ISPs (like Cogent or Level3) sell to both legitimate corporations AND massive server farms.

The Verdict: Because it is hard to tell the difference, Ad Networks often treat ALL "Business" ASNs as **"Potential Datacenter/Bot"** traffic by default. It is a "guilty until proven innocent" system.

第二，广告商认为 business 类型没有价值。Advertisers pay for clicks because they want to sell something. Ad algorithms have trillions of data points on conversion rates.

Residential/Mobile IP User: High probability of buying. They are at home, relaxed, often on a personal device. Value: $$$

Corporate/Business IP User: Low probability of buying.

- The Context: They are at work. They might click an ad for "Funny T-Shirts," but are they going to pull out their credit card and buy it right now while their boss might walk by? Usually, no.
- The Device: Often a company-owned laptop with firewalls, restricted permissions, or **monitoring software**.
- Value: $ (or $0).

The Result: Ad networks often **pre-filter Business IPs** (classifying them as "Non-Performing") to save money for their advertisers. If your bot forces them to serve ads to these IPs, you are destroying their conversion metrics.

第三，business 类型的流量会影响你帐号的质量。比如你有 1/3 流量来自 business，太高了，你的账号会被直接封掉。Including Business IPs in your rotation lowers your overall "Traffic Quality Score" and makes you look like a server farm.

#### Other

- Different types of IP address have different reputation

  - Residential
  - Datacenter
  - Mobile

- Same IP address should not send too many requests

### Passive TCP/IP Fingerprint

#### 检测原理

Most proxies (SOCKS5, HTTP, HTTPS CONNECT) work at the Application or Session layer (Layer 5/7), not the Packet layer (Layer 3).

Your Chain: You -> Proxy -> Website

The Process:

- Leg 1: Your machine performs a TCP Handshake with the Proxy Server. (The Proxy sees your fingerprint).
- The Request: You tell the proxy "Please connect me to https://www.google.com/search?q=google.com".
- Leg 2: The Proxy Server opens a new, separate TCP connection to Google.
- The Handshake: The Proxy sends its own SYN packet to Google to start this new connection.

**Result: The website sees the Proxy Server's TCP/IP Fingerprint (TTL, Window Size, MSS, etc.).**

Since most proxy servers run on Linux, the website usually sees a Linux TCP fingerprint.

#### 检测工具和结果

- p0f

  p0f is dead.

- zardaxt

  https://github.com/NikolaiT/zardaxt

  We can get OS type with this tool.

  Chrome OS，安卓用的都是 linux 内核，得分可能比 linux 还高一点。但是一般代理商不会在代理服务器上用 chrome os 或者安卓。

#### 例外：Firewall

Passive TCP fingerprinting has one major weakness: The Network "Mangles" Packets.

The Scenario: A legitimate user is on a real Windows PC at a University or Corporate Office.

The "Mangle": Their connection goes through a massive Corporate Firewall (e.g., Cisco/Palo Alto) before hitting the internet.

The Result: The Corporate Firewall **rewrites** the TCP headers for security.

It normalizes the TTL. It changes the Window Size.

The False Positive: To Cloudflare, this legitimate Windows user now looks like a "Cisco Router" or "Linux Firewall."

Because of this, Cloudflare cannot block solely on TCP fingerprints.

#### 解决方法：Spoofing

Because the "Linux Proxy vs. Windows User-Agent" mismatch is such a common detection method, high-end proxy providers (specifically Mobile Proxy sellers) have started adding a feature called "TCP/IP Fingerprint Spoofing" (or "Passive OS Masquerading").

How it works: The proxy server is configured to intentionally "mangle" its outgoing packets to look like Windows or macOS.

What they change: They force the Linux server to send a TTL of 128 (Windows) instead of 64 (Linux) and change the TCP Window Size to mimic a desktop OS.

#### 安全公司是否采用

https://blog.cloudflare.com/introducing-the-p0f-bpf-compiler/

这种方式是最有效、最容易的检测方式。In fact, Cloudflare has publicly blogged about how they took the open-source p0f tool and compiled it into BPF (Berkeley Packet Filter) bytecode so it can run directly inside the Linux Kernel of their edge servers. This allows them to check the TCP fingerprint of every single packet that hits their network at lightning speed without slowing down traffic.

#### 判断是否被检测

没办法，检测在服务器端进行。

### TLS Fingerprint

#### 检测原理

Transport Layer Security (TLS) is an end-to-end encryption protocol used in all HTTPS connections. HTTP clients perform the TLS handshake differently, leading to a unique fingerprint called JA3. If the generated fingerprint is different from the the regular browsers, it can lead to web scraping blocking.

- TLS data can be read with Wireshark

- client hello

  At the beginning of every HTTPS connection the client and the server needs to greet each other and negotiate the way connection will be secured.

  This is called "Client Hello" handshake.

  - TLS version

  - Cipher suites

    This field is a list of what encryption algorithms the negotiating parties support

  - Enabled extensions

    These extensions signify features the client supports, and some metadata like server domain name.

- JA3 fingerprint

  As we can see there are several values that can vary vastly across clients.

  For this, JA3 fingerprint technique is often used which essentially is a string of the varying values:

  ```
  TLSVersion,
  Ciphers,
  Extensions,
  support_groups(previously EllipticCurves),
  EllipticCurvePointFormats,
  ```

  Each value is separated by a `,` and array values are separated by a `-`.

  JA3 fingerprints are often further md5 hashed to reduce fingerprint length

- Browser

  When we're scraping using Playwright, Puppeteer or Selenium we're using real browsers, so we get genuine TLS fingerprints which is great!

  That being said, when scraping at scale using diverse collection of browser/operating-system versions can help to spread out connection through multiple fingerprints rather than one.

  Generally, running browsers in headless mode (be it Selenium, Playwright or Puppeteer) should not change TLS fingerprint. Meaning JA3 and other TLS fingerprinting techniques cannot identify whether connecting browser is headless or not.

#### 检测工具和结果

- Fingerprint type

  - JA3
  - JA4

- **What can be inferred from JA3/JA4 fingerprint**

  - SSL/TLS Engine

    Chrome/Edge use BoringSSL. Firefox uses NSS. Because these libraries were written by different teams, they have different "habits" when they say hello to a server.

    With this, we can detect whether the browser is firefox or chrome.

    But identifying Chrome vs. Edge vs. Brave is very hard. Because Microsoft Edge and Brave are both built on Chromium, they also use the BoringSSL library.

    This is why "Anti-Detect Browsers" usually give you a "Chromium-based" fingerprint. It is safe to pretend to be Chrome, Edge, or Brave using the same fingerprint.

  - Browser version

    Different versions of browsers support different encryption methods (Ciphers) and features (Extensions).

  - Cannot detect OS

    Modern browsers (like Chrome) bring their own TLS libraries with them. Chrome on Windows, Chrome on macOS, and Chrome on Linux all use the same internal BoringSSL library. Therefore, their JA3 fingerprints are often identical across operating systems.

#### 解决方法

Only by using high-quality anti-detect browsers or specialized libraries (like curl_cffi or uTLS) that replicate the browser's TLS behavior byte-for-byte.

#### 安全公司是否采用

It is a fundamental pillar of Cloudflare's security architecture. It is running on **every request**.

In fact, Cloudflare is one of the primary reasons TLS fingerprinting became an industry standard. Because they see roughly 20% of all internet traffic, they have the world's largest dataset of "Normal" vs. "Abnormal" TLS fingerprints.

Here is exactly how they and other major companies deploy it.

1 Cloudflare: The "Fingerprint Database"

Cloudflare doesn't just look at your fingerprint in isolation. They compare it against a massive global list.

- The "Known Good" List: They know exactly what Chrome 125 on Windows looks like (JA3/JA4 hash). If your fingerprint matches this whitelist, you pass this specific check.
- The "Known Bad" List: They have the fingerprints for every major hacking tool, scraper library, and botnet.
  - Python Requests: 33c... (Block)
  - Go-http-client: a0e... (Block)
  - Selenium (Default): ... (Block)
- The "Impersonators" List: This is the most dangerous one for you. If you send a User-Agent that says "Chrome" but your TLS fingerprint matches "Python," Cloudflare flags this as "Anomaly: Impersonation" and blocks it instantly.

2 AWS WAF: It's a Native Feature

As of late 2023, Amazon Web Services (AWS) added native JA3 fingerprinting to their Web Application Firewall (WAF).

This means any website hosted on AWS can click a single button to enable a rule that says:

"Block any request where the JA3 Fingerprint matches known bot libraries."

This is no longer "secret tech" used only by experts; it is a standard checkbox for millions of website administrators.

---

- **How does website use TLS fingerprint**

  - Is this JA3 hash on the Malware Blocklist?

    Yes: BLOCK.

  - Does this JA3 hash match the User-Agent claimed?

    JA3 中得到的浏览器类型、版本，和 user agent 要对得上。

    No (e.g., Python pretending to be Chrome): BLOCK.

  - Is this JA3 hash extremely rare/unique?

    Yes: CAPTCHA / Challenge.

  - If all pass: Allow traffic.

#### 判断是否被检测

没办法，检测在服务器端进行。

### Latency Detection

#### 检测原理：TCP Timing

Step 1: The Request (No Timer Yet)

- User (Proxy): Sends SYN packet.
- Server: Receives SYN.
- Action: The server allocates memory for this connection but does not start the RTT timer yet. It doesn't know how far away you are.

Step 2: The Challenge (Start Timer)

- Server: Sends a SYN-ACK (Synchronize-Acknowledge) packet back to the user.
- Action: The Kernel records the Timestamp.
  - Let's say: T1 = 10:00:00.000
- Meaning: "I just sent a packet to this IP. Let's see how long it takes to come back."

Step 3: The Reply (Stop Timer)

- User (Proxy): Receives the SYN-ACK. The OS kernel on the proxy is hard-coded to immediately send an ACK (Acknowledgement) packet back.
- Server: Receives the ACK.
- Action: The Kernel records the Timestamp.
  - Let's say: T2 = 10:00:00.020

Step 4: The Calculation 20ms - 0ms = 20ms

The web server (e.g., NGINX or Cloudflare) can query its own Linux Kernel (using a command like `tcp_info`) to get this exact number: `tcpi_rtt`.

#### 检测原理：Websocket Timing

Step 0: Setup

The website loads a JavaScript file into your browser. This script creates a WebSocket connection to the server.

Step 1: The Browser Starts the Stopwatch

- Actor: Your Browser (JavaScript running on your local machine).
- Action: The script records the exact current time in microseconds.
  - `const startTime = performance.now();`
- Action: Immediately after starting the timer, the Browser sends a small message (a "Ping") into the WebSocket tunnel.

Step 2: The Outward Journey

- Actor: The Network.
- Action: The message travels from Your House -> Your Proxy -> The Website Server.
- Note: This takes time (e.g., 75ms) because of the physical distance.

Step 3: The Server Acts as a Mirror

- Actor: The Website Server.
- Action: The server receives the message.
- Action: It does not process it or think about it. It is programmed to immediately "bounce" the message back to you.
- Note: The server adds almost zero delay here. It is just a mirror.

Step 4: The Return Journey

- Actor: The Network.
- Action: The reply travels from The Website Server -> Your Proxy -> Your House.
- Note: This takes another chunk of time (e.g., 75ms).

Step 5: The Browser Stops the Stopwatch

- Actor: Your Browser (JavaScript).
- Action: The Browser receives the reply message.
- Action: The script immediately records the end time.
  - `const endTime = performance.now();`

Step 6: The "Gotcha" (Reporting the Result)

- Actor: Your Browser.
- Action: The script calculates the total time:
  - Total RTT = endTime - startTime (e.g., 150ms).
- Action: The Browser sends this result back to the Server: "Hey Server, it took me 150ms to hear back from you."

#### 检测原理：Final Comparison

The Server now has two numbers on its desk:

- The TCP Ping: "I (The Server) measured the connection to the IP address. It took 10ms."
- The WebSocket Report: "The Browser just told me it took 150ms to verify the connection."

Server's Conclusion:

"The IP address is close (10ms), but the Browser is far away (150ms). This user is hiding behind a proxy."

#### 检测原理：TCP Timing Jitter

While RTT is the "speed" (10ms vs 150ms), Jitter is the "variance" of that speed over time.

**Datacenter TCP RTT**: If your TCP RTT is exactly 10.00ms, 10.01ms, 10.00ms... that is the "Flat Line" (Datacenter Jitter) we discussed.

**Residential TCP RTT**: If it is 35ms, 42ms, 29ms, 150ms... that is the "Messy Line" (Residential Jitter).

So, security systems look at both:

- RTT Mismatch: Proves you are hiding behind a proxy.
- Low Jitter in TCP Timing: Proves that proxy is a server in a datacenter, not a real home connection.

#### 检测原理：具体数值

| Scenario | Physical Distance | Typical RTT Range |
| - | - | - |
| Same City          | < 50 miles     | 5ms – 20ms     |
| Same State/Region  | < 300 miles    | 15ms – 40ms    |
| Cross-Country (US) | NY ↔ LA        | 60ms – 90ms    |
| Trans-Atlantic     | NY ↔ London    | 80ms – 130ms   |
| Trans-Pacific      | LA ↔ Tokyo     | 120ms – 200ms  |
| Global / Remote    | Brazil ↔ Japan | 250ms – 400ms+ |

1 The "Perfect Match" (Same City / State)

- Scenario: Your Proxy is in a New York datacenter. You are physically in New York (or running a VPS in New York).
- TCP Ping (Proxy): ~2ms.
- WebSocket Ping (You): ~5ms to 15ms.
- The Mismatch: ~10ms.
- Verdict: SAFE. This difference is indistinguishable from normal home Wi-Fi lag.

2 The "Regional" Variance (Same Continent)

- Scenario: Your Proxy is in New York. You are in Texas or Florida.
- TCP Ping (Proxy): ~2ms.
- WebSocket Ping (You): ~45ms.
- The Mismatch: ~40ms.
- Verdict: USUALLY SAFE.
  - Security systems generally allow a "Country-Level" buffer. A 40ms delay is common for a user whose ISP has bad routing. It is suspicious, but rarely an instant block.

3 The "Cross-Ocean" Giveaways (The Danger Zone)

- Scenario: Your Proxy is in New York. You are in London or Germany.
- TCP Ping (Proxy): ~2ms.
- WebSocket Ping (You): ~90ms.
- The Mismatch: ~88ms.
- Verdict: FLAGGED.
  - There is no residential ISP in New York that has a 90ms ping to a server also in New York. The physics don't add up.

4 The "Cross-World" Suicide (Asia to US)

- Scenario: Your Proxy is in New York. You are in China or Vietnam.
- TCP Ping (Proxy): ~2ms.
- WebSocket Ping (You): ~250ms (Going through the Great Firewall + Pacific Ocean).
- The Mismatch: ~248ms.
- Verdict: INSTANT BLOCK.
  - This is the easiest detection in the world. A 250ms delay implies you are on the other side of the planet.

The "Jitter" Factor (How to look real)

It's not just about being fast; it's about being consistently inconsistent.

- Real Residential: 20ms, 24ms, 19ms, 80ms (lag spike), 21ms.
- Real Mobile (5G): 30ms, 35ms, 45ms, 32ms.
- Bad Proxy: 150ms, 150ms, 151ms, 150ms. (Flatline).

#### 解决方法

- 选一个近的代理

  本地机器 -> 代理 -> 网站

  让本地机器到代理的物理距离尽可能短。

- 直接把代理当作本地机器

  代理 -> 网站

  直接在代理服务器上运行软件。

#### 安全公司是否采用

The "Big 3" (Cloudflare, Akamai, DataDome): YES. They have the scale to handle the data and the sophisticated ML models to filter out false positives.

Mid-Tier WAFs (Generic WordPress Plugins, Basic Firewalls): NO. They usually stick to simpler checks (IP reputation lists, basic User-Agent blocking). Implementing a WebSocket handshake for every visitor is too heavy for them.

Custom Enterprise Security: YES. Banks and airlines often implement this specifically to catch account-takeover bots that use residential proxies.

This detection is used because:

- It requires no database: They don't need to know if your IP is on a blacklist.
- It requires no "AI": It is just Time B - Time A. Simple math.
- It catches high-quality proxies: It works better against expensive residential proxies than cheap ones (because the latency gap is clearer).

This detection is not used because:

- The Starlink Problem: A Starlink user has a ground station (IP) that might be hundreds of miles from their actual house. Their "TCP Ping" (to the ground station) is fast, but their "WebSocket Ping" (to space and back) is slow.
  - Result: They look exactly like a Proxy User.
- The Corporate VPN Problem: An employee working from home might VPN into their HQ. Their IP is the HQ (fast line), but their browser is at home (slow line).
  - Result: They look like a bot.

The Solution: Companies like Cloudflare have to maintain massive "Allowlists" of Starlink IP ranges and Corporate VPNs to prevent banning millions of real users. Smaller security companies cannot maintain these lists accurately, so they turn this feature OFF by default to avoid complaints.

#### 如何判断是否被检测

If you want to know if a site is running this on you, look at your **Developer Tools -> Network Tab**.

- Filter for "WS" (WebSockets).
- Look for a connection that opens immediately on page load but sends almost no data (or just tiny binary blobs).
- If you see a payload like {"t": 1709...} (a timestamp) or a binary ping immediately followed by a closure, you just passed the latency test.

### JavaScript Fingerprint

JavaScript-based fingerprinting applies when web scraping with a headless browser automation tool, such as Selenium, Playwright, and Puppeteer. Since these web scraping tools are JavaScript-enabled, the target website can execute remote code on the client's machine. This remote code execution can reveal several details about the client, such as the:

- Hardware capabilities
- JavaScript runtime details
- Web browser information
- Operating system information

#### Browser Automation Tool Leaks

Many web-browser automation tools leak information about themselves to javascript execution context - meaning javascript can easily tell the browser is being controlled by a program rather than a human being.

- `navigator.webdriver`

#### How is fingerprint collected

Sites employ multiple levels and different approaches to collect browser fingerprints. However, they all have one thing in common: they are using a script written in JavaScript to evaluate the target browser's context and collect information about it (oftentimes also storing it in their database, or in a cookie).

To add, detailed fingerprinting is a resource intensive operation and most websites cannot afford to have their users wait there 2 seconds for the content to load.

#### What makes a fingerprint

- From HTTP header

- From window properties

  - `window.screen`
  - `window.navigator`

- From function calls

- With canvases

  Hash value depends on OS's rendering engines, GPUs, GPU drivers, browser engines, fonts, anti-aliasing algorithms.

  This value is a unique fingerprint value for your machine.

  - Create an HTML5 `<canvas>` Element

  - Draw Complex Graphics

    The script issues a specific set of drawing commands to the canvas. This isn't just a simple square. To maximize uniqueness, it typically involves:

    Text: Writing a specific string (e.g., "A_unique_string!@#$%") with a specific font, size, and style.

    Shapes & Gradients: Drawing complex shapes, lines, and color gradients.

    Emojis: Emojis are excellent for this because their rendering is highly dependent on the operating system.

  - Extract the Image Data

    After the hidden image is drawn, the script calls the `canvas.toDataURL()` function. This function converts the binary pixel data of the rendered image into a Base64-encoded text string.

  - Generate the Fingerprint (Hashing)

    The Base64 string is very long. To create a simple, manageable ID, this string is "hashed." A hashing function (like SHA-256) runs the long string through an algorithm and outputs a short, fixed-length string, like a47f7...f3d91.

- With WebGL

  A WebGL fingerprinting script collects two types of data

  - Querying Direct Parameters (The "Claim")

    This is the most important part. The script doesn't have to "guess" your hardware; it can just ask for it. It creates a WebGL context and starts reading parameters directly from your GPU's driver.

    Key parameters collected:

    - UNMASKED_RENDERER_WEBGL

      This is the "money shot." It's a string that explicitly names your GPU, like "NVIDIA GeForce RTX 4090/PCIe/SSE2", "Apple M2", or "Intel(R) Iris(R) Xe Graphics". This is the exact string we discussed that provides the "claim."

    - UNMASKED_VENDOR_WEBGL

      This names the company, e.g., "NVIDIA Corporation", "Apple", "Intel", or "Google Inc. (ANGLE)".

    - Hardware Limits

      The script queries dozens of specific limits that vary by GPU, such as:

      - MAX_TEXTURE_SIZE (e.g., 16384)
      - MAX_VERTEX_ATTRIBS (e.g., 16)
      - MAX_VIEWPORT_DIMS
      - MAX_RENDERBUFFER_SIZE

    - Supported Extensions

      It gets a list of all supported WEBGL_ extensions, which reveals specific capabilities of your driver.

    - Shader Precision

      It checks the precision (number of bits) available for a-la-carte shaders.

  - Part 2: Rendering a 3D Scene (The "Verification")

    This part is very similar to canvas fingerprinting, but in 3D.

    - The script renders a complex but invisible 3D scene using specific shaders, vertices, and lighting.

    - The way your specific GPU/driver combination computes the 3D math (anti-aliasing, shader calculations) results in subtle, unique pixel variations in the final rendered image.

    - The script calls `gl.readPixels()` to extract the pixel data from the scene.

    - It hashes this pixel data, just like a canvas fingerprint.

- From AudioContext

  Hash value depends on OS, browser implementation, hardware/drivers.

  This value is a unique fingerprint value for your machine.

  - Create a "Virtual Sound Card"

    The script uses the `OfflineAudioContext` API. This is the key. It's a "virtual" audio processing environment that does not send sound to your speakers. It's designed to process audio as fast as possible in the background and return a result.

  - Generate a Signal

    It creates a simple, mathematical sound wave using an `OscillatorNode`. This is like a perfect, computer-generated "tuning fork" sound (e.g., a 1,000 Hz sine wave).

  - Process the Signal

    This is where the "uniqueness" is created. The script pipes this perfect signal through one or more effects, most commonly a `DynamicsCompressorNode`. This compressor squashes the signal's dynamic range based on complex internal rules.

  - Read the Output

    The script renders this short audio clip inside the virtual context. It then reads the resulting audio data back as an array of numbers (a `Float32Array` of sample data).

  - Calculate the Hash

    The script takes this long array of numbers (e.g., ~5,000 samples) and "hashes" it into a single, simple fingerprint. A common method is to just sum all the values in the array.

- Font

  The final fingerprint is a simple list of "yes" or "no" answers (or just the list of "yes" answers) for the entire list, which is then hashed into a single ID.

  - Create Hidden Text

    A script on the website creates a tiny, invisible string of text (e.g., "mmmmmmmmmmlli") off-screen.

  - Set a "Fallback" Font

    It first sets the font for this text to a generic, built-in font, like "monospace", and measures the exact pixel width of the text. This is the "control" measurement.

  - Test a Font

    The script then changes the font-family property. It asks the browser to render the text with a specific "test font" (like "Arial") first, and sets the generic "monospace" font as the fallback.

    `font-family: "Arial", "monospace";`

  - Measure Again

    The script re-measures the pixel width of the text.

    - If the font is NOT installed

      The browser can't find "Arial", so it "falls back" to "monospace". The width of the text will be identical to the "control" measurement.

    - If the font IS installed

      The browser renders the text in "Arial". Since "Arial" has different letter shapes from "monospace", the width will be different.

  - Build the Fingerprint

    The script does this hundreds of times in milliseconds, testing a huge list of common and rare fonts ("Helvetica", "Times New Roman", "Segoe UI", "Calibri", "Roboto", etc.).

- From BatteryManager

#### How does website server handle fingerprint data

- Step 1: The "Packet" Arrives

  The server receives your "fingerprint packet," which includes:

  - User-Agent: (e.g., Windows 11 / Chrome 120)
  - WebGL Renderer: (e.g., NVIDIA GeForce RTX 4090)
  - Canvas Hash: (e.g., a47f7...f3d91)
  - Audio Hash: (e.g., 124.043...)
  - Font List: (e.g., ["Segoe UI", "Calibri", "Arial", ...])
  - IP Address: (e.g., 123.45.67.89)
  - ...and many more (screen resolution, timezone, etc.)

  Your initial Trust Score: 100/100

- Step 2: Consistency check

  The detective checks if your "documents" are forgeries by seeing if they contradict each other.

  - Failed

    Detective sees (User-Agent): "Okay, he says he's from Windows 11..."

    Detective sees (WebGL): "And he says he has an NVIDIA GeForce RTX 4090..."

    Detective sees (Fonts): "Wait. His font list is ["San Francisco", "Helvetica", "Menlo"]. These are macOS fonts. Windows doesn't have these."

    Detective sees (Canvas): "And his canvas hash is c99d2...8a1b5. My database knows this hash pattern is generated by Apple M2 GPUs, not NVIDIA."

    (The last step is done with ML models. The model analyzes the patterns in the hash and gives a probabilistic score: "I am 99.8% confident this hash was generated by an 'NVIDIA 40-series GPU'.")

  - A hash value is used too many times

    Detective sees: User-Agent: Windows 11, WebGL: NVIDIA 4090, Canvas: a47f7...f3d91

    Detective thinks: "This profile is perfect. All fingerprints are 100% consistent."

    Detective checks database: "Hold on. I've seen this exact canvas hash a47f7...f3d91 10,000 times in the last hour from 10,000 different IPs. A real person's hash is unique. This is a 'public' or 'stolen' document."

  - Real human

    Detective sees: User-Agent: Windows 11, WebGL: NVIDIA 4090, Canvas: 2b3a8...e4c1f (A hash it has never seen before)

    Detective thinks: "This profile is perfect. All fingerprints are 100% consistent."

    Detective checks database: "I have never seen this canvas hash 2b3a8...e4c1f before."

#### Detect when fingerprint is collected

Because of how common it has become to obfuscate fingerprinting scripts, there are many extensions that help identify fingerprinting scripts due to the fact that browser fingerprinting is such a big privacy question.

### DNS 泄漏

### Commercial Security Network

网站一般不会自己开发代码检查 bot，一般是通过商用解决方案比如 cloudflare 来检查 bot。

这些商用解决方案的检查手段一定非常成熟，以 cloudflare 为例：

- JA3/JA4 (TLS): Cloudflare heavily relies on JA3 and JA4 fingerprinting. They process ~20% of the entire internet's traffic, so they have the world's largest database of "normal" fingerprints. If your TLS fingerprint is "Unique" (rare), they challenge you immediately.

- TCP/IP: They analyze the TTL and Window Size of every packet entering their network edge.

- Canvas/JS: Their "Turnstile" challenge (the "Checking your browser..." screen) runs active JavaScript checks to verify your graphics card and mouse movement.

业内做的比较好的安全公司有：

- Cloudflare
- Akamai
- DataDome

## 流量伪装

### 代理供应商

首先需要了解代理供应商提供的网络流量特征。

https://datadome.co/bot-management-protection/how-proxy-providers-get-residential-proxies/

https://www.novada.com/blog-ordinary/the-core-difference-and-application-scenarios-between-static-isp-and-rotating-residential-proxies/

#### 静态代理：ip 来源

Most Static Residential IPs are created through a business deal between a **Proxy Provider** and a **Consumer ISP**.

- The ISP (e.g., AT&T, Comcast, or a regional ISP): They have millions of IPs.
- The Proxy Provider: They have servers in a datacenter.
- The Deal: The Proxy Provider pays the ISP to "announce" a block of IPs (e.g., a `/24` subnet) but route the traffic **physically** to the Proxy Provider's datacenter servers.

How it looks in databases:

- WHOIS/RIR: The ISP uses a mechanism called SWIP (Shared Whois Project) to register that specific block with the ISP's name (e.g., "Comcast Cable").
- The Result: When `ipinfo.io` or a website checks the IP, they see `ASN: Comcast` and `Type: ISP`.
- The Reality: The **physical** cable goes into a rack in a data center, not a house.

#### 静态代理：数据移动链路

Your machine -> proxy server -> target website

When they give you `1.2.3.4:8000:user:pass`, here is what is happening on their end:

- The Server: They have a physical Linux server (or VM) sitting in that datacenter.
- The Interface: They bind the "Residential" IP (1.2.3.4) to that server's network card.
- The Software: They run proxy software (like Squid or 3proxy) on that server.
  - It listens on port `8000`. It sees your attempt to connect to `1.2.3.4` and accept.
  - It checks your `user:pass` against an internal list.
  - It routes your outgoing traffic through `1.2.3.4`.

#### 动态代理：数据移动链路

Residential proxy providers do not give you a direct list of 10 million IP addresses. Instead, they give you a single Gateway Address (e.g., `us-geo.provider.com:8000`).

Your machine -> gateway / entry node -> exit node -> target website

Here is the chain of events when you make a request:

- Step A: You Connect to the Gateway (The "Entry Node")

  What it is: A massive, high-speed server located in a Datacenter (e.g., AWS or Google Cloud). This is often called the "Super Proxy" or "Load Balancer."

  What happens: You send your request here. The connection is fast (low latency) because this server is built for speed.

  The "Mask": This Gateway handles your authentication (Username/Password) and decides which Exit Node to assign you based on your request (e.g., "Give me a US IP").

- Step B: The Gateway Tunnels to the Exit Node

  The Search: The Gateway looks at its live pool of millions of connected devices and picks one (e.g., Bob’s Android phone in Texas).

  The Tunnel: The Gateway sends your request through a pre-established, encrypted tunnel to Bob’s phone.

  Latency Spike: This is where the lag happens. The data has to travel from the Datacenter Gateway to a random consumer device on a (potentially slow) home Wi-Fi or 4G network.

- Step C: The Exit Node Hits the Target

  The Request: Bob’s phone receives the instruction and makes the actual HTTP request to google.com.

  The Appearance: Google sees the request coming from Bob's Residential IP (Comcast/AT&T). It has no idea the Gateway or You exist.

#### 动态代理：Exit Nodes 来源

- The mobile "SDK" Model (Ethical)

  This is how legitimate, big-name providers operate. They effectively "buy" bandwidth from regular users.

  The Deal: A developer makes a free app (e.g., a Free VPN, a casual game, or a weather app).

  The SDK: The developer installs a "Monetization SDK" (like Honeygain, Peer2Profit, or Bright Data SDK) into the app.

  The Consent: When a user installs the app, the Terms of Service say: "Allow us to use your idle bandwidth in exchange for an Ad-Free experience."

  The Result: When the user's phone is charging and on Wi-Fi, it quietly connects to the Proxy Gateway and starts routing traffic for customers like you. The user gets a free app; you get a residential IP.

- Browser extensions

  Proxy providers contact popular browser extension developers, offering payment to include their proxy code in app updates. This approach works because browser extensions have broad permissions and run constantly in the background, while users rarely read privacy policies or understand what permissions they’re granting.

  Security researchers from GitLab found that compromised extensions affected over 3.2 million users in early 20253. Extensions marketed as ad blockers, VPNs, and productivity tools secretly routed traffic through users’ connections.

- The "Botnet" Model (Unethical / Illegal)

  This is how cheap, "unlimited bandwidth" providers often operate.

  Malware: Hackers infect routers, smart TVs, ip cameras, or fridges with malware (like Mirai).

  Forced Proxying: These devices are turned into zombie proxies without the owner knowing.

  Risk: These IPs are often flagged faster because they behave erratically and send spam.

  常见被黑的设备包括：router, firewall, WAP, gateway, broadband router, webcam, security-misc, DVR, media device, storage-misc。

- Mobile proxy farm

  专门提供移动代理的商家一般都是使用自己的设备，要么是很多台手机，要么是很多台可插 sim 卡的 4g 模块。

### 设备伪装

#### Windows VS Mac

Mac 不同产品线都有一个特点，配置确定的情况下，所有机器的硬件都是一样的。比如最低配的 Mac mini m4，世界上所有的机器，硬件都是一样的。


#### 检测移动设备伪装

**If you can pass CreepJS with a high trust score, you are beating 99% of detections.**

There are absolutely tools and specific techniques to detect this. In fact, distinguishing a "Fake Mobile" (desktop spoofing Android) from a "Real Mobile" is one of the easiest checks for modern anti-fraud systems.

Because your underlying hardware (Intel CPU, NVIDIA GPU, wired power source) is physically different from a phone's hardware (ARM CPU, Adreno/Mali GPU, battery), your browser leaks these differences in dozens of tiny ways.

1 The "Silver Bullet" Detection Tools

You can check your own browser against these tools to see if you are leaking:

- BrowserLeaks (WebGL & JavaScript): Go to browserleaks.com/webgl. If the "Unmasked Renderer" says "NVIDIA", "AMD", or "Intel", you are 100% busted. Real Android phones use "Adreno" (Qualcomm), "Mali" (Samsung/MediaTek), or "PowerVR".

- CreepJS: A rigorous fingerprinting tool that looks for "lies" in your browser environment. It will explicitly flag "Worker Mismatch" or "Platform Mismatch" if your spoofing is incomplete.

- DeviceInfo.me: Provides a deep dive into your sensor data. If your accelerometer and gyroscope data is `null` or perfectly static, it knows you are on a desktop.

2 How They Detect You (The Technical Vectors)

Here are the specific signals security systems use, ranked from easiest to hardest to fix.

- The GPU Lie (WebGL)

  This is the most common giveaway.

  The Check: The website asks your browser to render a 3D graphic and checks the GPU name string.

  Real Android: Adreno (TM) 740 or Mali-G710.

  Your Spoof: NVIDIA GeForce RTX 4070 or Intel UHD Graphics.

  Verdict: Phones do not have desktop RTX cards. Instant Block.

  Fix: Your anti-detect browser must allow you to "Rename" the WebGL Vendor/Renderer.

- The Sensor Lie (Gyroscope/Accelerometer)

  Mobile phones are always moving slightly (micro-jitters), even when sitting on a table. Desktops are perfectly still.

  The Check: The site listens to `DeviceOrientationEvent` and `DeviceMotionEvent`.

  Real Android: Returns constant streams of changing data for alpha/beta/gamma rotation (e.g., 0.00231, -0.0019).

  Your Spoof: Returns `null`, `undefined`, or a perfectly static `0` that never changes.

  Fix: Advanced anti-detect browsers inject "Noise" (fake random jitter) into these APIs.

- The Battery Lie

  The Check: `navigator.getBattery()`.

  Real Android: `charging: false`, `level: 0.89` (variable).

  Your Spoof: `charging: true`, `level: 1.0` (100%).

  Verdict: A device that is permanently 100% charged and plugged in is usually a server or desktop.

- The Touch Lie (`maxTouchPoints`)

  The Check: `navigator.maxTouchPoints`.

  Real Android: Returns `5` or `10` (multitouch).

  Your Spoof: Often returns `0` or `1` if you are just using Chrome DevTools "Device Mode" without a specialized tool.

  Note: Even if you spoof this to "5", some tests check for Touch Events (`ontouchstart`). If you click with a mouse, the event has "mouse-like" properties (no pressure, precise radius) that differ from a fat finger tap.

### 各类检测手段对代理流量的检测

- IP

  静态代理的 IP 一般就是 ISP IP，不用过多担心。

  动态代理的 IP 可能各种类型都有，要看供应商的好坏，比如 business isp mobile。同时不同 ip 检测商给出的检测结果也不一样。

  移动代理是一种特殊的动态代理，ip 是手机运营商分配的，只可能是 mobile 类型。

  business 类型的 ip 最好不要用。

- TCP/IP fingerprint

  这个问题比较棘手。target website 得到的 TCP/IP fingerprint 一般是链路中最后一环的 fingerprint。

  静态代理链路中的最后一环一般是 linux 机器。

  动态代理链路中的最后一环，各种机器都有可能，要看供应商的好坏，比如安卓设备、amazon echo、windows 设备。

  移动代理链路中的最后一环，一般都是安卓设备。另外移动代理一般会提供 tcp/ip spoofing，原因是移动代理对设备有直接控制权，可以获得 root 权限，更改内核空间。而动态代理对链路中最后一环的设备没有这么深的控制。

- TLS fingerprint

  target website 得到的 TLS fingerprint 是链路开头的 fingerprint。链路开头就是指纹浏览器或者 BAS 用的 CEF。

  另外安全公司一般只能从 TLS fingerprint 中获取浏览器的种类和版本（通过 SSL/TLS library 判断），不能获取操作系统。

  使用指纹浏览器时，user agent 里的 chrome 版本要和实际浏览器用的 chrome 引擎版本对上。不然很容易就露馅了。

- Latency detection

  这个问题同样棘手。TCP timing 是链路中的最后一环到网站的时间。Websocket timing 是整条链路的时间。

  静态代理的链路一般是：my machine -> proxy server -> target website。我们可以缩短 machine 到 proxy server 的物理距离，或者直接在 proxy server 上进行软件操作。

  但是静态代理有一个非常大的问题：因为代理服务器在数据中心中，网络设施比较好，TCP Timing 非常小而且基本不变。这和普通用户不符。普通用户因为各种原因，TCP timing 会来回波动。

  动态代理的链路一般是：my machine -> gateway -> exit node -> target website。我们可以缩短 my machine 到 exit node 的物理距离，让 my machine gateway exit node 都在一个区域（尽量不要距离太远，小国家跨国可以，但是比如美国，从美西到美东，距离太远了，会有明显 latency）。

  移动代理的链路一般是：TODO。

  如果 my machine 在 CN，还要在链路中加一个代理，那情况更是雪上加霜。

- Javascript fingerprint

  通过 bablosoft 动态指纹或者指纹浏览器，一般很好解决。

- 静态 ip 解决方案

  买来的静态 ip 基本 tcp/ip 指纹全是 linux，加上 tcp timing 没有波动，模仿不了真实用户。

  - 解决方案一：用家庭宽带真实机器

    租用远程家庭宽带 windows 物理机器，不使用指纹浏览器。

    淘宝上有很多国内的机器，最低价一个月 50。CN ip 应该可以直接访问广告联盟网站。

    台湾虾皮上搜索「遠端主機 租賃」、「遠端主機 模擬器多開 出租」。

    其他地区，包括国外的很难找。

    租用远程家庭宽带 mac mini 机器也可以，不使用指纹浏览器。

    淘宝上有很多，基本 200 一个月。

    租用真实手机也可以。

  - 解决方案二：用家庭宽带真实机器加指纹浏览器

  - 解决方案三：windows vps + 指纹浏览器模拟 windows 用户 + 移动 ip

    用 tcp/ip spoofing 把 tcp/ip 指纹改成 windows 的。在网站看来，就是使用移动 ip 的 windows 用户。

  - 解决方案四：windows vps + 指纹浏览器模拟安卓手机 + 移动 ip。

    在网站看来，就是使用移动 ip 的安卓用户。

- 动态 ip 解决方案

  - chrome on windows -> 住宅代理 -> 网站

    网站看到：linux/安卓系统，chrome 某个版本 tls 指纹，windows user agent，卒。

  - chrome on windows -> 移动代理 -> 网站

    网站看到：linux/安卓系统，chrome 某个版本 tls 指纹，windows user agent，卒。

  - **chrome on windows -> 带 tcp/ip spoofing 的移动或者住宅代理 -> 网站**

    网站看到：windows 系统，chrome 某个版本 tls 指纹，windows user agent，好。

    ip 是移动或者住宅都可以。

  - 模拟安卓上的 chrome -> 住宅代理 -> 网站

    网站看到：linux/安卓系统，chrome 某个版本 tls 指纹，安卓 user agent。

    但是，安卓手机不能使用住宅 ip，卒。

  - **模拟安卓上的 chrome -> 移动代理 -> 网站**

    网站看到：linux/安卓系统，chrome 某个版本 tls 指纹，安卓 user agent。

    ip 也是移动 ip，好。

### 浏览器热身

"Building a small history of browsing" (often called "Cookie Profile Building" or "Account Warm-up") is the process of making your browser look "lived-in" before you visit your target link.

When you open a fresh Chrome instance in your automation software, it is "sterile." It has no cookies, no cache, no history, and no "Ad Interest" profile.

Ad networks (like Google Ads, Taboola, Outbrain) hate sterile browsers. A user with zero history who appears out of nowhere, clicks an ad, and disappears is the #1 signature of a bot.

Here is the technical breakdown of what "building history" actually does and why your 1-minute plan is risky.

1. The "Cookie Sync" (The Most Important Part)

Ad networks track users across the internet.

- Real User: Visits nytimes.com, then youtube.com, then amazon.com.
  - On New York Times, Google/Doubleclick drops a cookie: ID=123.
  - On YouTube, Google sees ID=123 again and adds "Likes News" to the profile.
  - On Amazon, Google sees ID=123 again and adds "Shopper" to the profile.
- Your Bot (Minute 1): Opens browser -> Visits Ad Link.
  - Google sees: "No Cookie ID." Creates ID=999.
  - Verdict: This is a brand new, unknown user. **Low Trust**.
- The Goal of "Building History":
  - Before visiting your target ad, your bot should visit 3-5 popular "High Trust" websites (e.g., CNN, Wikipedia, Amazon, Reddit).
  - Why? These sites have ad trackers on them. By visiting them first, you pick up the tracking cookies before you hit the target ad. When you finally land on the target page, the ad network sees: "Ah, this is the user we just saw on CNN and Reddit. They are real."

2. Chrome's Local "Topics API"

Modern Chrome doesn't just rely on cookies; it builds an internal profile of you called the Privacy Sandbox (Topics API).

- Chrome analyzes the pages you visit and stores "Topics" locally (e.g., "Sports," "Technology").
- When an ad loads, the browser tells the ad network: "My user is interested in Sports."
- Your Bot: Has visited 0 pages. Chrome tells the ad network: "No topics found."
- Verdict: Suspicious. Real humans always have topics.

3. The "Referrer" Chain

"Building history" also means fixing how you arrive at the page.

- Direct Access (Bad): Opening the browser and pasting the link.
  - Referrer: (none)
- Organic Access (Good): Visiting Google, searching for a keyword related to the video, and clicking a result.
  - Referrer: https://www.google.com/

## Web Scraping Tools

- Tools to get official IP info

  - https://lookup.icann.org/en/lookup
  - https://www.arin.net/

- **Tools for dns leak**

  - https://browserleaks.com/dns
  - https://ipleak.net/
  - https://whoer.net/dns-leak-test

- **Tools to get IP asn and company (网页端)**

  - https://ipinfo.io/pricing
  - ping0.cc
  - ipapi.is

- **Tools for proxy/vpn detection**

  https://proxydetect.live/

- **Tools to get passive TCP/IP fingerprint**

  - https://browserleaks.com/tcp
  - https://proxydetect.live/

- **Tools to test IP address reputation**

  - https://www.ipqualityscore.com/
  - https://scamalytics.com/ 本机运行
  - https://ipfighter.com/ 本机运行
  - https://www.ipjiance.com/
  - https://www.ip111.cn/ 没什么用

- **综合检查**

  - https://iphey.com/
  - https://whoer.net/

- **Tools to test TLS fingerprint**

  - https://scrapfly.io/web-scraping-tools/ja3-fingerprint
  - https://browserleaks.com/tls

- Tools to detect browser fingerprint collection

  https://github.com/freethenation/DFPM

- Tools to get javascript fingerprint

  - https://abrahamjuliot.github.io/creepjs/
  - https://fingerprintjs.github.io/fingerprintjs
  - https://browserleaks.com/
  - https://scrapfly.io/web-scraping-tools/browser-fingerprint

- Bot detection

  https://scrapfly.io/blog/posts/how-to-avoid-web-scraping-blocking-javascript#leak-detection-tools

  https://github.com/TheGP/untidetect-tools?tab=readme-ov-file#detection-tests

  - https://datadome.co/guides/bot-protection/anti-bot-solution/: DataDome’s bot protection solution examines hundreds of signals simultaneously: browser fingerprints, timing patterns, mouse movements, request sequences, and device characteristics
  - https://github.com/fingerprintjs/BotD
  - https://bot.sannysoft.com/

## Web Scraping Mitigations

https://github.com/TheGP/untidetect-tools

https://github.com/niespodd/browser-fingerprinting

- Ensure HTTP header, IP address, js fingerprint variable (location, timezone) all match

- IP Address

  Rotating proxy pool with residential IPs

- Javascript fingerprint leaking

  - How to manually patch

    To patch these leaks in our browser automation tools we can take advantage of page initiation script functionality

  - Javascript fingerprint generator

    - browserforge

      reimplementation of Apify's fingerprint-suite

      https://github.com/daijro/browserforge

    - fingerprint-suite

      https://github.com/apify/fingerprint-suite

- Browser automation libraries with stealth ability

  - Selenium

    - undetected-chromedriver (Last updated Feb 18, 2024)

      https://github.com/ultrafunkamsterdam/undetected-chromedriver

      https://pypi.org/project/undetected-chromedriver/

  - **SeleniumBase** (Actively updated, 11.8k)

    https://github.com/seleniumbase/SeleniumBase

    https://pypi.org/project/seleniumbase/

  - Puppeteer

    - puppeteer-extra-plugin-stealth (Not maintained anymore)

      https://github.com/berstend/puppeteer-extra/tree/master/packages/puppeteer-extra-plugin-stealth

  - Playwright

    - **patchright** (Actively maintained, 1.8k)

      https://github.com/Kaliiiiiiiiii-Vinyzu/patchright

  - **nodriver** (Actively maintained, 3.1k)

    successor of the undetected-chromedriver, only works with chrome, does not require selenium to work.

    https://github.com/ultrafunkamsterdam/nodriver

    https://pypi.org/project/nodriver/

  - **zendriver** (Actively maintained, 865)

    Fork of ultrafunkamsterdam/nodriver.

    https://github.com/cdpdriver/zendriver

    https://pypi.org/project/zendriver/

  - **Camoufox**

    https://github.com/daijro/camoufox (Author has been hospitalized since March 2025, 4k)

    https://github.com/coryking/camoufox (Actively maintained fork)

- **Crawlee**

  https://crawlee.dev/

  Might be detected if `PuppeteerCrawler` or `PlaywrightCrawler` is used.

- Scraping services

  https://www.hyperbrowser.ai/

  https://scrapfly.io/

## Ad Alliance Automation Implementation

- 自动化方法

  - 用 browser automation frameworks

    两个 youtuber 都是这么做的。

  - 用 embedded engine 自己开发软件

    不太现实，cef fingerprinting 都没有现成的库

  - 用 Playwright/Puppeteer+stealth+fingerprint

  - 用 Playwright/Puppeteer + Kameleo

- Browser automation frameworks

  - BAS

    卖给别人，需要 premium，40$/6 个月。

    实际使用 CEF。

  - ZennoPoster

- Browser automation libraries

  - Playwright
  - Puppeteer
  - Selenium

- Embedding browser engine

  - Chromium Embedded Framework (CEF)

    The gold standard. This is the open-source project for embedding Chromium into other applications. It has bindings for many languages, including C# (CefSharp), Python (cefpython), and Go.

  - Microsoft Edge WebView2

    The modern Microsoft solution for embedding the Edge (Chromium) engine into .NET and C++ Windows applications.

  - WebKit

    The engine for Safari can also be embedded, (e.g., WKWebView on macOS/iOS or WebKitGTK on Linux).

- Fingerprint browsers

  Use broswers like AdsPower, Hubstudio, etc.

  Too expansive. Kameleo 不错。

  - Hubstudio 5000 次环境打开：480 元/月

  - Gologin 5000 unique profiles：449$/月

    https://gologin.com/pricing/

  - Incognition 5000 配置：500$/月

    https://incogniton.com/zh-hans/pricing-zh-hans/

  - Multilogin 5000 配置：687$/月

    https://multilogin.org/pricing

  - Morelogin 5000 环境数：560$/月

    https://www.morelogin.com/zh/pricing/

  - AdsPower 5000 环境：602$/月

    https://www.adspower.net/pricing

  - Dolphin anty 5000 profiles：1135$/月

    https://dolphin-anty.com/tarifs/

  - Octo browser 5000 profiles：1089€/月

    https://octobrowser.net/zh/pricing/

  - Kameleo 10 concurrent browsers, unlimited profile storage €59/月

    https://kameleo.io/pricing
