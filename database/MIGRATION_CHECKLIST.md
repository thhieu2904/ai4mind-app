# ✅ MIGRATION CHECKLIST

Checklist đầy đủ cho việc migration database. In ra và check off khi hoàn thành mỗi bước.

---

## 📋 PHASE 0: PLANNING & PREPARATION

### Team Review & Approval

- [ ] **Tech Lead** đã review toàn bộ kế hoạch
- [ ] **Product Manager** đã approve timeline
- [ ] **Backend team** đã đọc CODE_UPDATE_GUIDE
- [ ] **Frontend team** đã review ảnh hưởng (minimal)
- [ ] **DevOps/DBA** đã review migration scripts
- [ ] **Management** đã approve downtime window
- [ ] Team meeting đã hoàn thành, Q&A đã clear

### Environment Setup

- [ ] **Staging environment** đã được setup giống production
- [ ] **Database credentials** đã được secure
- [ ] **Backup storage** có đủ dung lượng (2x DB size)
- [ ] **Monitoring tools** đã được setup (Sentry, DataDog, etc.)
- [ ] **Alerting** đã được configure cho DB errors
- [ ] **Communication channels** ready (Slack, Discord, etc.)

### Documentation Review

- [ ] Đã đọc `EXECUTIVE_SUMMARY.md`
- [ ] Đã đọc `SCHEMA_ANALYSIS_AND_IMPROVEMENT_PLAN.md`
- [ ] Đã đọc `CODE_UPDATE_GUIDE.md`
- [ ] Đã review tất cả migration scripts
- [ ] Đã hiểu rollback plan

### Tools & Access

- [ ] **PostgreSQL client** đã cài (psql, pg_dump)
- [ ] **Supabase dashboard** access
- [ ] **Production DB** credentials (có sẵn nhưng secure)
- [ ] **Staging DB** credentials
- [ ] **Git repository** access
- [ ] **Deployment tools** ready (GitHub Actions, CI/CD)

---

## 📋 PHASE 1: PRE-MIGRATION (1-2 ngày trước)

### Backup Strategy

- [ ] **Full database backup** của production
  ```bash
  pg_dump -h db.xxxx.supabase.co -U postgres -d postgres > backup_full_production.sql
  ```
- [ ] **Verify backup** có thể restore
  ```bash
  pg_restore -l backup_full_production.sql
  ```
- [ ] **Store backup** ở nhiều nơi (local, cloud, external drive)
- [ ] **Document backup location** và password

### Staging Testing

- [ ] **Clone production data** to staging
- [ ] **Run migration 001** trên staging
- [ ] **Verify indices** được tạo correctly
- [ ] **Test queries** performance improvement
- [ ] **Run migration 002** trên staging
- [ ] **Verify timestamps** được add
- [ ] **Run migration 003** trên staging (CRITICAL)
- [ ] **Verify all IDs** migrated to BIGINT
- [ ] **Test all relationships** (JOINs, FKs)
- [ ] **Run migration 004** trên staging
- [ ] **Verify constraints** work
- [ ] **Test invalid data** rejected

### Code Preparation

- [ ] **Backend code** updated theo CODE_UPDATE_GUIDE
  - [ ] All models: Integer → BigInteger
  - [ ] Timestamps added to models
  - [ ] Error handling for constraints
  - [ ] Pydantic schemas updated
- [ ] **Frontend code** reviewed (minimal changes)
- [ ] **Tests** passing locally
- [ ] **Code reviewed** by team
- [ ] **Git branch** created: `database-improvement-phase1`
- [ ] **PR ready** nhưng chưa merge

### Communication

- [ ] **Users notified** về maintenance window
  - [ ] Email sent 3 days before
  - [ ] In-app notification 1 day before
  - [ ] Website banner 1 day before
- [ ] **Team calendar** đã block maintenance window
- [ ] **On-call schedule** arranged
- [ ] **Rollback team** identified và available
- [ ] **Status page** prepared (if applicable)

---

## 📋 MIGRATION DAY: EXECUTION

### T-2 Hours: Final Checks

- [ ] **Full backup** chạy lại lần cuối
  ```bash
  pg_dump > backup_final_before_migration_$(date +%Y%m%d_%H%M%S).sql
  ```
- [ ] **Team on call** và sẵn sàng
- [ ] **Monitoring dashboards** open và watching
- [ ] **Rollback scripts** ready
- [ ] **Communication channels** active
- [ ] **Application health check** - all green
- [ ] **No other deployments** planned
- [ ] **Database activity** low (verified)

### T-30 Minutes: Pre-Migration

- [ ] **Announce maintenance** start
- [ ] **Enable maintenance mode** (if applicable)
- [ ] **Stop background workers** (if applicable)
- [ ] **Final health check** of application
- [ ] **Final backup verification**
- [ ] **Take screenshot** of current metrics

### T-0: Migration 001 (Add Indices)

⏱️ Expected: 5-10 minutes | Downtime: NO

- [ ] **Start time** recorded: ****\_\_****
- [ ] **Run migration 001**
  ```bash
  psql -h db.xxxx.supabase.co -U postgres -d postgres < migrations/001_add_indices.sql
  ```
- [ ] **Verify indices** created
  ```sql
  SELECT indexname FROM pg_indexes WHERE schemaname = 'public' AND indexname LIKE 'idx_%';
  ```
- [ ] **Test query performance** (should be faster)
- [ ] **Check errors** in logs
- [ ] **End time** recorded: ****\_\_****
- [ ] **Duration**: ****\_\_**** minutes
- [ ] **Status**: ✅ Success / ❌ Failed

**If failed:**

- [ ] **Run rollback** script
- [ ] **Investigate** error
- [ ] **Decide**: retry or abort?

### T+15: Migration 002 (Add Timestamps)

⏱️ Expected: 1-2 minutes | Downtime: NO

- [ ] **Start time** recorded: ****\_\_****
- [ ] **Run migration 002**
  ```bash
  psql < migrations/002_add_timestamps.sql
  ```
- [ ] **Verify columns** added
  ```sql
  SELECT column_name FROM information_schema.columns
  WHERE table_schema = 'public' AND column_name IN ('created_at', 'updated_at');
  ```
- [ ] **Verify triggers** created
- [ ] **Test UPDATE** query updates `updated_at`
- [ ] **End time** recorded: ****\_\_****
- [ ] **Status**: ✅ Success / ❌ Failed

### T+20: Migration 003 (Migrate IDs to BIGINT)

⏱️ Expected: 30-60 minutes | Downtime: YES ⚠️

**🚨 CRITICAL MIGRATION - HIGH ATTENTION REQUIRED**

- [ ] **Start time** recorded: ****\_\_****
- [ ] **Application stopped** (if not already)
- [ ] **All connections closed** (except migration)
- [ ] **Run migration 003**
  ```bash
  psql < migrations/003_migrate_ids_to_bigint.sql
  ```
- [ ] **Watch progress** in console (should print each step)
- [ ] **Verify all IDs** are BIGINT
  ```sql
  SELECT table_name, column_name, data_type
  FROM information_schema.columns
  WHERE table_schema = 'public' AND column_name LIKE '%id%';
  ```
- [ ] **Verify sequences** are BIGINT
- [ ] **Verify foreign keys** recreated
- [ ] **Test INSERT** with new IDs
- [ ] **Test JOINs** between tables
- [ ] **End time** recorded: ****\_\_****
- [ ] **Duration**: ****\_\_**** minutes
- [ ] **Status**: ✅ Success / ❌ Failed

**If failed:**

- [ ] **CRITICAL:** Restore from backup immediately
- [ ] **Investigate** error thoroughly
- [ ] **DO NOT PROCEED** to next migrations

### T+90: Migration 004 (Add CHECK Constraints)

⏱️ Expected: 5-10 minutes | Downtime: NO

- [ ] **Start time** recorded: ****\_\_****
- [ ] **Run pre-migration validation** (trong script)
- [ ] **Fix invalid data** if any found
- [ ] **Run migration 004**
  ```bash
  psql < migrations/004_add_check_constraints.sql
  ```
- [ ] **Verify constraints** added
  ```sql
  SELECT conname FROM pg_constraint WHERE conname LIKE 'check_%';
  ```
- [ ] **Test constraint violations** (should fail with proper message)
- [ ] **End time** recorded: ****\_\_****
- [ ] **Status**: ✅ Success / ❌ Failed

### T+105: Deploy New Code

- [ ] **Merge PR** với updated models
- [ ] **Deploy backend** to production
- [ ] **Wait for deployment** to complete
- [ ] **Health check** endpoints
- [ ] **Test critical flows**:
  - [ ] User registration
  - [ ] Student login
  - [ ] Create assessment
  - [ ] Voice analysis upload
  - [ ] AI chat
  - [ ] Counselor conversations
- [ ] **Check error logs** for any issues
- [ ] **Verify metrics** in monitoring

### T+120: Post-Migration Checks

- [ ] **All migrations** completed successfully
- [ ] **Application running** normally
- [ ] **No errors** in logs
- [ ] **Performance metrics** improved
- [ ] **User testing** successful
- [ ] **Disable maintenance mode**
- [ ] **Announce completion** to users

---

## 📋 POST-MIGRATION (24-48 hours)

### Day 1: Monitoring

- [ ] **Hour 1:** Check logs every 15 minutes
- [ ] **Hour 2-4:** Check logs every 30 minutes
- [ ] **Hour 5-24:** Check logs every 2 hours
- [ ] **Error rate** within normal range
- [ ] **Response times** improved or same
- [ ] **No user complaints** about data issues
- [ ] **Database size** as expected
- [ ] **Backup running** automatically

### Day 2-7: Verification

- [ ] **Performance metrics** collected
  - [ ] Query response times
  - [ ] Index usage
  - [ ] Database CPU/memory
- [ ] **Compare before/after** metrics
- [ ] **User feedback** collected
- [ ] **No data integrity issues** reported
- [ ] **All features** working correctly

### Week 2: Optimization

- [ ] **Identify unused indices** (if any)
  ```sql
  SELECT indexname, idx_scan FROM pg_stat_user_indexes
  WHERE schemaname = 'public' AND idx_scan = 0;
  ```
- [ ] **Tune queries** using new indices
- [ ] **Update documentation** with learnings
- [ ] **Team retrospective** meeting

---

## 📋 DOCUMENTATION & CLEANUP

### Code Documentation

- [ ] **Update README** với new schema info
- [ ] **Update API docs** (if needed)
- [ ] **Update ERD diagram** (if exists)
- [ ] **Document learnings** từ migration
- [ ] **Update runbook** với actual timings

### Team Knowledge Share

- [ ] **Post-mortem meeting** scheduled
- [ ] **Share findings** với team
- [ ] **Update best practices** doc
- [ ] **Train team members** on new constraints
- [ ] **Document gotchas** và solutions

### Cleanup

- [ ] **Old backups** moved to archive (keep for 90 days)
- [ ] **Staging environment** cleaned up
- [ ] **Temporary files** deleted
- [ ] **Git branch** merged và deleted
- [ ] **Credentials** rotated (security)

---

## 🚨 ROLLBACK PLAN (If Needed)

### Immediate Rollback (During Migration)

- [ ] **Stop migration** immediately
- [ ] **Note error message** và state
- [ ] **Restore from backup**
  ```bash
  pg_restore backup_final_before_migration_*.sql
  ```
- [ ] **Verify data integrity** after restore
- [ ] **Restart application** with old code
- [ ] **Notify users** về issue
- [ ] **Schedule post-mortem** meeting

### Post-Migration Rollback (If Issues Found Later)

- [ ] **Assess severity** of issue
- [ ] **Decide rollback window**
- [ ] **Notify users** về rollback
- [ ] **Run rollback scripts** (if available)
  ```bash
  psql < migrations/004_add_check_constraints_rollback.sql
  psql < migrations/002_add_timestamps_rollback.sql
  psql < migrations/001_add_indices_rollback.sql
  # Migration 003 CANNOT rollback - must restore from backup
  ```
- [ ] **Or restore from backup** (full rollback)
- [ ] **Revert code changes** (redeploy old version)
- [ ] **Verify system** working with old state
- [ ] **Investigate** root cause
- [ ] **Plan retry** với fixes

---

## 📊 METRICS TO TRACK

### Before Migration

- [ ] **Average query time**: ****\_\_**** ms
- [ ] **P95 query time**: ****\_\_**** ms
- [ ] **P99 query time**: ****\_\_**** ms
- [ ] **Database size**: ****\_\_**** GB
- [ ] **Index size**: ****\_\_**** GB
- [ ] **Active connections**: ****\_\_****
- [ ] **Slow query count**: ****\_\_****/day

### After Migration

- [ ] **Average query time**: ****\_\_**** ms (target: 50% improvement)
- [ ] **P95 query time**: ****\_\_**** ms
- [ ] **P99 query time**: ****\_\_**** ms
- [ ] **Database size**: ****\_\_**** GB (expected: +5-10%)
- [ ] **Index size**: ****\_\_**** GB (expected: +20-30%)
- [ ] **Active connections**: ****\_\_****
- [ ] **Slow query count**: ****\_\_****/day (target: 50% reduction)

### Improvement %

- [ ] **Query time improved**: ****\_\_****%
- [ ] **Index usage**: ****\_\_****% of queries
- [ ] **Constraint violations caught**: ****\_\_**** (first week)
- [ ] **User satisfaction**: ****\_\_**** (survey)

---

## ✅ SIGN-OFF

### Pre-Migration Sign-off

- [ ] **Tech Lead**: ******\_****** Date: **\_\_\_**
- [ ] **DBA/DevOps**: ******\_****** Date: **\_\_\_**
- [ ] **Product Manager**: ******\_****** Date: **\_\_\_**

### Post-Migration Sign-off

- [ ] **Tech Lead**: ******\_****** Date: **\_\_\_**
- [ ] **DBA/DevOps**: ******\_****** Date: **\_\_\_**
- [ ] **Product Manager**: ******\_****** Date: **\_\_\_**

**Migration Status:** ✅ Success / ⚠️ Partial / ❌ Failed / 🔄 Rolled Back

**Final Notes:**

```
[Space for any final notes, learnings, or issues encountered]




```

---

**Document Version:** 1.0  
**Last Updated:** 2025-10-07  
**Migration Date:** ******\_\_\_******  
**Completed By:** ******\_\_\_******
