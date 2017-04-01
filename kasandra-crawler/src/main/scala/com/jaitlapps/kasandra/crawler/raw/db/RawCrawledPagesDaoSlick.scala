package com.jaitlapps.kasandra.crawler.raw.db

import java.util.UUID

import com.jaitlapps.kasandra.crawler.db.DbConnection
import com.jaitlapps.kasandra.crawler.models.SiteType
import com.jaitlapps.kasandra.crawler.raw.db.table.RawCrawledPage
import com.jaitlapps.kasandra.crawler.raw.db.table.RawCrawledPagesTable
import com.jaitlapps.kasandra.crawler.wall.db.table.WallLink
import com.jaitlapps.kasandra.crawler.wall.db.table.WallLinksTable

import scala.concurrent.Future

class RawCrawledPagesDaoSlick(
  override val dbConnection: DbConnection
) extends RawCrawledPagesDao
  with RawCrawledPagesTable
  with WallLinksTable {
  import dbConnection.profile.api._

  private val db = dbConnection.db

  override def save(raw: RawCrawledPage): Future[Int] = db.run {
    rawCrawledPagesQuery += raw
  }

  override def markAsParsed(id: UUID): Future[Int] = db.run {
    rawCrawledPagesQuery
      .filter(_.id === id)
      .map(_.isParsed)
      .update(true)
  }

  override def crawledPagesWithLink(siteType: SiteType): Future[Seq[(RawCrawledPage, WallLink)]] = {
    val query = rawCrawledPagesQuery
      .filter(_.siteType === siteType)
      .join(wallLinkQuery)
      .on(_.linkId === _.id)

    db.run(query.result)
  }
}