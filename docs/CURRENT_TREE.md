.
├── apps
│   ├── companies
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── __init__.py
│   │   ├── migrations
│   │   │   ├── 0001_initial.py
│   │   │   └── __init__.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   └── views.py
│   ├── contacts
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── __init__.py
│   │   ├── migrations
│   │   │   ├── 0001_initial.py
│   │   │   └── __init__.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   └── views.py
│   ├── core
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── __init__.py
│   │   ├── labels.py
│   │   ├── migrations
│   │   │   ├── 0001_initial.py
│   │   │   └── __init__.py
│   │   ├── models.py
│   │   ├── runtime_settings.py
│   │   ├── templatetags
│   │   │   ├── __init__.py
│   │   │   └── label_filters.py
│   │   └── ui_semantics.py
│   ├── crm_update_engine
│   │   ├── entrypoints.py
│   │   ├── events.py
│   │   ├── __init__.py
│   │   └── services.py
│   ├── dashboard_views.py
│   ├── emailing
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── decision_detail.py
│   │   ├── __init__.py
│   │   ├── management
│   │   │   ├── commands
│   │   │   │   ├── crm_pipeline_report.py
│   │   │   │   ├── demo_email_flow.py
│   │   │   │   └── __init__.py
│   │   │   └── __init__.py
│   │   ├── migrations
│   │   │   ├── 0001_initial.py
│   │   │   ├── 0002_remove_emailthread_linked_company_and_more.py
│   │   │   ├── 0003_alter_outboundemail_options_and_more.py
│   │   │   ├── 0004_outboundemail_email_type.py
│   │   │   ├── 0005_inboundemail.py
│   │   │   ├── 0006_outboundemail_source_inbound.py
│   │   │   ├── 0007_inboundinterpretation_inbounddecision.py
│   │   │   ├── 0008_inbounddecision_automation_fields.py
│   │   │   ├── 0008_outboundemail_source_recommendation.py
│   │   │   ├── 0009_merge_0008_emailing_branches.py
│   │   │   └── __init__.py
│   │   ├── models_patch_smll.py
│   │   ├── models.py
│   │   ├── services
│   │   │   ├── decision_automation.py
│   │   │   ├── email_processing_patch.py
│   │   │   ├── inbound_analysis_service.py
│   │   │   ├── inbound_decision_apply_service.py
│   │   │   ├── inbound_decision_engine.py
│   │   │   ├── inbound_interpreter.py
│   │   │   ├── inbound_simulator.py
│   │   │   ├── mail_provider_service.py
│   │   │   ├── outbound_sender.py
│   │   │   ├── provider_router.py
│   │   │   ├── recommendation_bridge.py
│   │   │   ├── reply_generator.py
│   │   │   └── smll_bootstrap.py
│   │   ├── smll_adapter.py
│   │   ├── templates
│   │   │   └── emailing
│   │   ├── test_decision_detail.py
│   │   ├── tests_crm_update_engine.py
│   │   ├── tests.py
│   │   ├── tests_smll_integration.py
│   │   ├── urls.py
│   │   ├── views_decision.py
│   │   └── views.py
│   ├── events
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── __init__.py
│   │   ├── migrations
│   │   │   ├── 0001_initial.py
│   │   │   ├── 0002_activityevent_delete_event.py
│   │   │   └── __init__.py
│   │   ├── models.py
│   │   ├── services.py
│   │   ├── tests.py
│   │   └── views.py
│   ├── external_actions
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── dispatcher.py
│   │   ├── __init__.py
│   │   ├── migrations
│   │   │   ├── 0001_initial.py
│   │   │   ├── 0002_rename_external_ac_intent__f9bc7f_idx_external_ac_intent__32184c_idx_and_more.py
│   │   │   ├── 0003_externalactionintent_tenant_scope.py
│   │   │   └── __init__.py
│   │   ├── models.py
│   │   ├── providers
│   │   │   ├── email_stub.py
│   │   │   └── __init__.py
│   │   ├── services
│   │   │   ├── approval.py
│   │   │   ├── core.py
│   │   │   ├── dispatcher.py
│   │   │   └── __init__.py
│   │   ├── services_legacy.py
│   │   ├── tests_approval.py
│   │   ├── tests_dispatcher.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── facts
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── __init__.py
│   │   ├── migrations
│   │   │   ├── 0001_initial.py
│   │   │   ├── 0002_remove_factrecord_confidence_and_more.py
│   │   │   └── __init__.py
│   │   ├── models.py
│   │   ├── services.py
│   │   ├── tests.py
│   │   └── views.py
│   ├── inferences
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── __init__.py
│   │   ├── migrations
│   │   │   ├── 0001_initial.py
│   │   │   ├── 0002_remove_inferencerecord_inference_value_and_more.py
│   │   │   └── __init__.py
│   │   ├── models.py
│   │   ├── services.py
│   │   ├── tests.py
│   │   └── views.py
│   ├── __init__.py
│   ├── knowledge
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── hooks.py
│   │   ├── __init__.py
│   │   ├── management
│   │   │   ├── commands
│   │   │   │   ├── harvest_knowledge.py
│   │   │   │   ├── __init__.py
│   │   │   │   └── review_knowledge_candidate.py
│   │   │   └── __init__.py
│   │   ├── migrations
│   │   │   ├── 0001_initial.py
│   │   │   └── __init__.py
│   │   ├── models.py
│   │   ├── services
│   │   │   ├── candidate_generator.py
│   │   │   ├── email_knowledge_extractor.py
│   │   │   ├── embedding_service.py
│   │   │   ├── embeddings.py
│   │   │   ├── extraction.py
│   │   │   ├── generator.py
│   │   │   ├── hooks.py
│   │   │   ├── __init__.py
│   │   │   ├── promotion.py
│   │   │   └── vector_memory.py
│   │   ├── signals.py
│   │   └── tests.py
│   ├── lead_research
│   │   ├── apps.py
│   │   ├── __init__.py
│   │   ├── migrations
│   │   │   ├── 0001_initial.py
│   │   │   └── __init__.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── services
│   │   │   ├── lead_promotion.py
│   │   │   └── signal_discovery.py
│   │   ├── tasks.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── opportunities
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── __init__.py
│   │   ├── management
│   │   │   ├── commands
│   │   │   │   ├── analyze_open_opportunities.py
│   │   │   │   ├── analyze_opportunity.py
│   │   │   │   ├── enrich_opportunities.py
│   │   │   │   ├── __init__.py
│   │   │   │   └── promote_tasks.py
│   │   │   └── __init__.py
│   │   ├── migrations
│   │   │   ├── 0001_initial.py
│   │   │   ├── 0002_initial.py
│   │   │   ├── 0003_opportunity_source_recommendation.py
│   │   │   ├── 0004_opportunity_last_analyzed_at.py
│   │   │   └── __init__.py
│   │   ├── models.py
│   │   ├── services
│   │   │   ├── autotasker.py
│   │   │   ├── context_builder.py
│   │   │   ├── enrichment.py
│   │   │   ├── __init__.py
│   │   │   ├── opportunity_analyzer.py
│   │   │   ├── prioritization.py
│   │   │   └── promote.py
│   │   ├── tasks.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   ├── views_prioritized.py
│   │   └── views.py
│   ├── providers
│   │   ├── base.py
│   │   ├── calendar_placeholder.py
│   │   ├── llm_embedded.py
│   │   ├── llm_gemini.py
│   │   ├── mail_embedded.py
│   │   ├── mail_m365.py
│   │   ├── mail_provider.py
│   │   ├── mail_registry_v2.py
│   │   ├── mail_runtime.py
│   │   ├── registry.py
│   │   └── tests
│   │       ├── test_mail_provider_service.py
│   │       └── test_mail_runtime.py
│   ├── recommendations
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── execution_actions.py
│   │   ├── execution_adapters.py
│   │   ├── execution_application.py
│   │   ├── execution.py
│   │   ├── __init__.py
│   │   ├── management
│   │   │   ├── commands
│   │   │   │   ├── backfill_opportunity_reviews.py
│   │   │   │   ├── crm_pipeline_report.py
│   │   │   │   ├── detect_opportunity_signals.py
│   │   │   │   └── __init__.py
│   │   │   └── __init__.py
│   │   ├── merge.py
│   │   ├── merge_runtime.py
│   │   ├── migrations
│   │   │   ├── 0001_initial.py
│   │   │   ├── 0002_alter_airecommendation_status.py
│   │   │   ├── 0003_airecommendation_source.py
│   │   │   ├── 0004_airecommendation_tenant_scope.py
│   │   │   └── __init__.py
│   │   ├── models.py
│   │   ├── nba.py
│   │   ├── opportunity_intelligence.py
│   │   ├── priority.py
│   │   ├── services
│   │   │   ├── action_loop.py
│   │   │   ├── external_actions.py
│   │   │   ├── factory.py
│   │   │   └── __init__.py
│   │   ├── services_engine.py
│   │   ├── services_llm.py
│   │   ├── services.py
│   │   ├── simulation.py
│   │   ├── tests_merge.py
│   │   ├── tests_nba.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   ├── views.py
│   │   └── views_simulation.py
│   ├── simulated_personas
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── __init__.py
│   │   ├── migrations
│   │   │   ├── 0001_initial.py
│   │   │   ├── 0002_rename_sim_persona_org_active_idx_simulated_p_operati_be4ec5_idx_and_more.py
│   │   │   └── __init__.py
│   │   ├── models.py
│   │   ├── runtime
│   │   │   ├── __init__.py
│   │   │   └── smll_engine.py
│   │   ├── services
│   │   │   ├── __init__.py
│   │   │   └── prompt_builder.py
│   │   ├── tests.py
│   │   └── tests_runtime.py
│   ├── strategy
│   │   ├── apps.py
│   │   ├── __init__.py
│   │   ├── services
│   │   │   ├── context_builder.py
│   │   │   ├── __init__.py
│   │   │   ├── llm_backends.py
│   │   │   ├── prompt_builder.py
│   │   │   ├── rule_based_engine.py
│   │   │   └── strategy_engine.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── tasks
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── __init__.py
│   │   ├── management
│   │   │   ├── commands
│   │   │   │   ├── __init__.py
│   │   │   │   ├── materialize_open_recommendations.py
│   │   │   │   ├── materialize_recommendations.py
│   │   │   │   └── reclassify_manual_tasks.py
│   │   │   └── __init__.py
│   │   ├── migrations
│   │   │   ├── 0001_initial.py
│   │   │   ├── 0002_alter_crmtask_task_type.py
│   │   │   ├── 0003_crmtask_opportunity_crmtask_source_and_more.py
│   │   │   ├── 0004_crmtask_is_revoked.py
│   │   │   └── __init__.py
│   │   ├── models.py
│   │   ├── services
│   │   │   └── materialize.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── tenancy
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── __init__.py
│   │   ├── migrations
│   │   │   ├── 0001_initial.py
│   │   │   ├── 0002_seed_default_orgs.py
│   │   │   ├── 0003_identity_and_corporate_domains.py
│   │   │   ├── 0004_alter_corporatedomain_options_and_more.py
│   │   │   └── __init__.py
│   │   ├── models.py
│   │   ├── services
│   │   │   ├── domain_resolution.py
│   │   │   └── __init__.py
│   │   └── tests_identity.py
│   ├── updates
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── conditions.py
│   │   ├── decision_output.py
│   │   ├── explainability.py
│   │   ├── __init__.py
│   │   ├── management
│   │   │   └── commands
│   │   │       ├── replay_diff.py
│   │   │       ├── replay_email.py
│   │   │       └── replay_version.py
│   │   ├── migrations
│   │   │   ├── 0001_initial.py
│   │   │   ├── 0002_remove_crmupdateproposal_approval_required_and_more.py
│   │   │   ├── 0003_ruleevaluationlog_and_more.py
│   │   │   └── __init__.py
│   │   ├── models.py
│   │   ├── rule_engine.py
│   │   ├── rule_sets.py
│   │   ├── rules_loader.py
│   │   ├── rules.py
│   │   ├── rules_registry.py
│   │   ├── rules_v1.py
│   │   ├── rules_v2.py
│   │   ├── services_diff.py
│   │   ├── services.py
│   │   ├── services_replay.py
│   │   ├── simulation.py
│   │   ├── test_decision_output.py
│   │   ├── tests.py
│   │   └── views.py
│   └── users
│       ├── admin.py
│       ├── apps.py
│       ├── __init__.py
│       ├── migrations
│       │   └── __init__.py
│       ├── models.py
│       ├── tests.py
│       └── views.py
├── apps.knowledge
├── autoheaders.py
├── backups
│   └── reco_ops_2026_03_09
│       ├── models.py.bak
│       └── views.py.bak
├── CHANGELOG.md
├── ch_test.sh
├── cleansession.sh
├── cleartmp.sh
├── config
│   ├── asgi.py
│   ├── celery.py
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── db.sqlite3
├── dev_verify_execute_contact_strategy.py
├── dev_verify_execute_followup.py
├── dev_verify_execute_reply_strategy.py
├── dev_verify_execute_unified.py
├── docker
├── docker-compose.yml
├── Dockerfile
├── docs
│   ├── BEHAVIOR_PROMPT.md
│   ├── CANONICAL_BACKEND.md
│   ├── CHANGELOG.md
│   ├── CURRENT_TREE.md
│   ├── CURRENT_TREE.txt
│   ├── DASHBOARD_STATUS_UPDATE.md
│   ├── decision_output.md
│   ├── GIT_STATUS.md
│   ├── HANDOFF_CURRENT.md
│   ├── NEXT_SESSION.md
│   ├── PROJECT_HEALTH_REPORT.md
│   ├── REQUIREMENTS_SNAPSHOT.txt
│   ├── ROADMAP_AI_COMMERCIAL_OS.md
│   ├── ROADMAP.md
│   ├── ROADMAP_V2_AI_COMMERCIAL_OS.md
│   ├── ROADMAP_V3_AI_COMMERCIAL_OS.md
│   ├── SESSION_LOG_2026_03_08.md
│   ├── SESSION_LOG_2026_03_09.md
│   ├── SESSION_LOG_2026_03_10.md
│   ├── SESSION_LOG_2026_03_11.md
│   ├── SESSION_LOG_2026_03_12.md
│   ├── SESSION_LOG_2026_03_23.md
│   ├── SESSION_LOG_2026_03_24.md
│   ├── SESSION_LOG_2026_03_25.md
│   ├── SESSION_LOG_2026_03_26.md
│   ├── SESSION_LOG_2026_03_27.md
│   ├── SESSION_LOG_2026_03_28.md
│   ├── SESSION_LOG_2026_03_29.md
│   ├── SESSION_LOG_2026_03_30_AUDIT.md
│   ├── SESSION_LOG_2026_03_30.md
│   ├── SESSION_LOG_2026_03_31.md
│   ├── SESSION_LOG_2026_04_01.md
│   ├── SESSION_LOG_2026_04_02.md
│   ├── SESSION_LOG_2026_04_02_V2_6.md
│   └── SESSION_LOG.md
├── dump_llm_context.sh
├── fcheck.sh
├── fix_dispatcher_module_v1.txt
├── fix_django_app_names.sh
├── flog.sh
├── frun.sh
├── HANDOFF_CURRENT.md
├── manage.py
├── NEXT_SESSION.md
├── output.txt
├── parche_opportunities_template_kpi.py
├── parche_opportunities_view.py
├── parche.py
├── patch_auto_dispatch_safe_intents.txt
├── patch_views_recommendations.py
├── refactor_inbox_intelligence_v2.sh
├── requirements
│   └── base.txt
├── runserver.log
├── scripts
├── services
│   ├── adapters
│   │   ├── __init__.py
│   │   └── m365
│   │       ├── calendar.py
│   │       ├── __init__.py
│   │       └── mail.py
│   ├── ai
│   │   ├── agents
│   │   │   └── __init__.py
│   │   ├── __init__.py
│   │   └── llm_client.py
│   ├── email_ingest.py
│   ├── events.py
│   ├── fact_extraction.py
│   ├── inference_engine.py
│   ├── __init__.py
│   ├── m365
│   │   ├── graph_client.py
│   │   └── __init__.py
│   ├── ports
│   │   ├── contracts.py
│   │   ├── idempotency.py
│   │   ├── __init__.py
│   │   ├── policy.py
│   │   ├── registry.py
│   │   ├── router.py
│   │   └── types.py
│   ├── update_proposals.py
│   └── workflows
│       └── __init__.py
├── static
│   └── app_ui
│       ├── css
│       │   ├── bootstrap.min.css
│       │   ├── clndr.css
│       │   ├── custom.css
│       │   ├── font-awesome.css
│       │   ├── jqvmap.css
│       │   ├── lines.css
│       │   ├── style.css
│       │   └── style.css.bak
│       ├── fonts
│       │   ├── FontAwesome.otf
│       │   ├── fontawesome-webfont.eot
│       │   ├── fontawesome-webfont.svg
│       │   ├── fontawesome-webfont.ttf
│       │   ├── fontawesome-webfont.woff
│       │   ├── fontawesome-webfont.woff2
│       │   ├── glyphicons-halflings-regular.eot
│       │   ├── glyphicons-halflings-regular.svg
│       │   ├── glyphicons-halflings-regular.ttf
│       │   ├── glyphicons-halflings-regular.woff
│       │   └── glyphicons-halflings-regular.woff2
│       ├── images
│       │   ├── 1.png
│       │   ├── 2.png
│       │   ├── 3.png
│       │   ├── 4.png
│       │   ├── 5.png
│       │   ├── arrow-left.png
│       │   ├── arrow-right.png
│       │   ├── bg.jpg
│       │   ├── cloud.png
│       │   ├── favicon.ico
│       │   ├── logo.png
│       │   ├── pic1.png
│       │   ├── pic2.png
│       │   ├── pic3.jpg
│       │   └── pic4.jpg
│       └── js
│           ├── bootstrap.min.js
│           ├── Chart.js
│           ├── clndr.js
│           ├── custom.js
│           ├── d3.v3.js
│           ├── jquery.min.js
│           ├── jquery.vmap.js
│           ├── jquery.vmap.sampledata.js
│           ├── jquery.vmap.world.js
│           ├── metisMenu.min.js
│           ├── moment-2.2.1.js
│           ├── rickshaw.js
│           ├── site.js
│           └── underscore-min.js
├── templates
│   ├── base.html
│   ├── dashboard
│   │   ├── home.html
│   │   ├── index.html
│   │   └── partials
│   │       ├── decision_transparency.html
│   │       ├── insight_list.html
│   │       ├── next_best_action.html
│   │       └── recommendation_card.html
│   ├── emailing
│   │   ├── decision_detail.html
│   │   ├── email_detail.html.legacy
│   │   ├── email_list.html.legacy
│   │   ├── inbox.html
│   │   ├── outbox.html
│   │   └── partials
│   │       ├── inbox_actions.html
│   │       ├── inbox_ai_panel.html
│   │       ├── inbox_decision_panel.html
│   │       ├── inbox_email_card.html
│   │       ├── inbox_empty.html
│   │       ├── inbox_filters.html
│   │       ├── inbox_header.html
│   │       └── inbox_stats.html
│   ├── lead_research
│   │   └── list.html
│   ├── opportunities
│   │   ├── list.html.legacy
│   │   ├── opportunity_tasks.html.legacy
│   │   └── prioritized.html
│   ├── partials
│   │   ├── app_nav.html
│   │   ├── app_sidebar.html
│   │   ├── app_topbar.html
│   │   └── design_system.html
│   ├── placeholders
│   ├── recommendations
│   │   ├── list.html
│   │   └── recommendation_list.html.legacy
│   ├── strategy
│   │   └── chat.html
│   └── tasks
│       └── list.html
├── testing.py
├── tests
└── typescript

101 directories, 503 files
