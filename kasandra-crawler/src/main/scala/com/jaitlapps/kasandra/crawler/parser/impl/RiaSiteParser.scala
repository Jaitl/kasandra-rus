package com.jaitlapps.kasandra.crawler.parser.impl

import com.jaitlapps.kasandra.crawler.parser.SiteParser
import org.jsoup.nodes.Document

object RiaSiteParser extends SiteParser {
  protected override def parseTitle(doc: Document): String = doc.select(".b-content-body h1.b-article__title").text()

  protected override def parseContent(doc: Document): String = {
    val content = doc.select(".b-content-body .b-article__body")

    val strong = content.select("strong")
    val spam = content.select("div.b-inject")

    if (!strong.isEmpty) {
      strong.remove()
    }

    if (!spam.isEmpty) {
      spam.remove()
    }

    if (content.text().startsWith(".")) {
      content.text().substring(1)
    } else {
      content.text()
    }
  }
}
