import sys
from types import ModuleType, SimpleNamespace

import pytest
from fastapi import HTTPException


def make_user(id="user-1", role="user", email="user@example.com"):
    return SimpleNamespace(
        id=id,
        role=role,
        email=email,
        name="Test User",
        profile_image_url="/user.png",
    )


def make_file(id="file-1", user_id="owner-1"):
    return SimpleNamespace(
        id=id,
        user_id=user_id,
        filename="secret.txt",
        path=None,
        meta={},
        data={},
    )


def make_request(**config_overrides):
    config = SimpleNamespace(
        BYPASS_EMBEDDING_AND_RETRIEVAL=True,
        ENABLE_RAG_HYBRID_SEARCH=False,
        TOP_K=3,
        **config_overrides,
    )
    return SimpleNamespace(
        app=SimpleNamespace(
            state=SimpleNamespace(
                config=config,
                EMBEDDING_FUNCTION=lambda *args, **kwargs: pytest.fail(
                    "embedding should not run before access checks"
                ),
            )
        ),
        headers={},
        cookies={},
    )


def import_retrieval(monkeypatch):
    if "open_webui.routers.retrieval" in sys.modules:
        return sys.modules["open_webui.routers.retrieval"]

    def stub_module(name, **attrs):
        module = ModuleType(name)
        for attr, value in attrs.items():
            setattr(module, attr, value)
        monkeypatch.setitem(sys.modules, name, module)
        return module

    stub_module(
        "open_webui.models.files",
        FileModel=object,
        Files=SimpleNamespace(),
    )
    stub_module(
        "open_webui.models.knowledge",
        Knowledges=SimpleNamespace(),
    )
    stub_module(
        "open_webui.utils.access_control",
        has_access=lambda *args, **kwargs: False,
    )
    stub_module(
        "open_webui.storage.provider",
        Storage=SimpleNamespace(get_file=lambda path: path),
    )
    stub_module(
        "open_webui.retrieval.vector.factory",
        VECTOR_DB_CLIENT=SimpleNamespace(),
    )
    stub_module(
        "open_webui.retrieval.loaders.main",
        Loader=object,
    )
    stub_module(
        "open_webui.retrieval.loaders.youtube",
        YoutubeLoader=object,
    )
    stub_module(
        "open_webui.retrieval.utils",
        get_embedding_function=lambda *args, **kwargs: None,
        get_model_path=lambda model, *args, **kwargs: model,
        query_collection=lambda *args, **kwargs: None,
        query_collection_with_hybrid_search=lambda *args, **kwargs: None,
        query_doc=lambda *args, **kwargs: None,
        query_doc_with_hybrid_search=lambda *args, **kwargs: None,
    )

    class SearchResult(SimpleNamespace):
        pass

    stub_module("open_webui.retrieval.web.main", SearchResult=SearchResult)
    stub_module(
        "open_webui.retrieval.web.utils",
        get_web_loader=lambda *args, **kwargs: None,
    )

    search_modules = {
        "brave": "search_brave",
        "kagi": "search_kagi",
        "mojeek": "search_mojeek",
        "bocha": "search_bocha",
        "duckduckgo": "search_duckduckgo",
        "google_pse": "search_google_pse",
        "jina_search": "search_jina",
        "searchapi": "search_searchapi",
        "serpapi": "search_serpapi",
        "searxng": "search_searxng",
        "yacy": "search_yacy",
        "serper": "search_serper",
        "serply": "search_serply",
        "serpstack": "search_serpstack",
        "tavily": "search_tavily",
        "bing": "search_bing",
        "exa": "search_exa",
        "perplexity": "search_perplexity",
        "sougou": "search_sougou",
        "firecrawl": "search_firecrawl",
        "external": "search_external",
    }
    for module_name, function_name in search_modules.items():
        stub_module(
            f"open_webui.retrieval.web.{module_name}",
            **{function_name: lambda *args, **kwargs: []},
        )

    from open_webui.routers import retrieval

    return retrieval


def test_trusted_header_auth_rejects_jwt_without_header(monkeypatch):
    from open_webui.utils import auth

    token = auth.create_token({"id": "user-1"})
    response = SimpleNamespace(deleted=[])
    response.delete_cookie = response.deleted.append
    request = SimpleNamespace(
        headers={},
        cookies={"token": token, "oauth_id_token": "oauth-token"},
        state=SimpleNamespace(enable_api_key=False),
    )

    monkeypatch.setattr(auth, "WEBUI_AUTH_TRUSTED_EMAIL_HEADER", "X-Forwarded-Email")
    monkeypatch.setattr(
        auth.Users,
        "get_user_by_id",
        lambda user_id: make_user(id=user_id, email="alice@example.com"),
    )

    with pytest.raises(HTTPException) as exc:
        auth.get_current_user(request, response, None, auth_token=None)

    assert exc.value.status_code == 401
    assert response.deleted == ["token", "oauth_id_token"]


def test_trusted_header_auth_allows_case_insensitive_match(monkeypatch):
    from open_webui.utils import auth

    token = auth.create_token({"id": "user-1"})
    request = SimpleNamespace(
        headers={"X-Forwarded-Email": "ALICE@EXAMPLE.COM"},
        cookies={"token": token},
        state=SimpleNamespace(enable_api_key=False),
    )
    response = SimpleNamespace(delete_cookie=lambda name: pytest.fail(name))
    user = make_user(id="user-1", email="alice@example.com")

    monkeypatch.setattr(auth, "WEBUI_AUTH_TRUSTED_EMAIL_HEADER", "X-Forwarded-Email")
    monkeypatch.setattr(auth.Users, "get_user_by_id", lambda user_id: user)

    assert auth.get_current_user(request, response, None, auth_token=None) == user


def test_process_file_rejects_cross_user_file_before_writes(monkeypatch):
    retrieval = import_retrieval(monkeypatch)

    victim_file = make_file(id="victim-file", user_id="owner-1")
    updates = []
    files = SimpleNamespace(
        get_file_by_id=lambda file_id: victim_file if file_id == victim_file.id else None,
        update_file_data_by_id=lambda *args: updates.append(("data", args)),
        update_file_hash_by_id=lambda *args: updates.append(("hash", args)),
        update_file_metadata_by_id=lambda *args: updates.append(("meta", args)),
    )
    knowledges = SimpleNamespace(
        get_knowledge_bases_by_user_id=lambda *args: [],
        get_knowledge_by_id=lambda *args: None,
    )

    monkeypatch.setattr(retrieval, "Files", files)
    monkeypatch.setattr(retrieval, "Knowledges", knowledges)

    with pytest.raises(HTTPException) as exc:
        retrieval.process_file(
            make_request(),
            retrieval.ProcessFileForm(file_id=victim_file.id, content="overwrite"),
            user=make_user(id="attacker-1"),
        )

    assert exc.value.status_code == 404
    assert updates == []


def test_process_file_allows_owner(monkeypatch):
    retrieval = import_retrieval(monkeypatch)

    owner = make_user(id="owner-1")
    owner_file = make_file(id="owner-file", user_id=owner.id)
    updates = []
    files = SimpleNamespace(
        get_file_by_id=lambda file_id: owner_file if file_id == owner_file.id else None,
        update_file_data_by_id=lambda *args: updates.append(("data", args)),
        update_file_hash_by_id=lambda *args: updates.append(("hash", args)),
        update_file_metadata_by_id=lambda *args: updates.append(("meta", args)),
    )
    knowledges = SimpleNamespace(
        get_knowledge_bases_by_user_id=lambda *args: [],
        get_knowledge_by_id=lambda *args: None,
    )

    monkeypatch.setattr(retrieval, "Files", files)
    monkeypatch.setattr(retrieval, "Knowledges", knowledges)

    result = retrieval.process_file(
        make_request(),
        retrieval.ProcessFileForm(file_id=owner_file.id, content="owner content"),
        user=owner,
    )

    assert result["status"] is True
    assert result["filename"] == owner_file.filename
    assert ("data", (owner_file.id, {"content": "owner content"})) in updates
    assert any(update[0] == "hash" for update in updates)


def test_query_doc_rejects_cross_user_file_collection_before_embedding(monkeypatch):
    retrieval = import_retrieval(monkeypatch)

    victim_file = make_file(id="victim-file", user_id="owner-1")
    files = SimpleNamespace(
        get_file_by_id=lambda file_id: victim_file if file_id == victim_file.id else None
    )
    knowledges = SimpleNamespace(
        get_knowledge_bases_by_user_id=lambda *args: [],
        get_knowledge_by_id=lambda *args: None,
    )

    monkeypatch.setattr(retrieval, "Files", files)
    monkeypatch.setattr(retrieval, "Knowledges", knowledges)

    with pytest.raises(HTTPException) as exc:
        retrieval.query_doc_handler(
            make_request(BYPASS_EMBEDDING_AND_RETRIEVAL=False),
            retrieval.QueryDocForm(
                collection_name=f"file-{victim_file.id}", query="secret"
            ),
            user=make_user(id="attacker-1"),
        )

    assert exc.value.status_code == 404
