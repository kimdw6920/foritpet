# 보안 점검 요약 (For It Pet)

## 세션·로그인

- **브라우저 종료 시 로그아웃**: `SESSION_EXPIRE_AT_BROWSER_CLOSE = True` — 브라우저를 완전히 닫으면 세션 쿠키가 제거됩니다.
- **시간 제한**: `SESSION_COOKIE_AGE` (기본 3600초 = 1시간). `SESSION_SAVE_EVERY_REQUEST = True` 로 요청마다 만료 시각이 갱신되어, 활동 중에는 세션이 유지됩니다.
- **쿠키**: `SESSION_COOKIE_HTTPONLY`, `SESSION_COOKIE_SAMESITE=Lax`.

## HTTPS (프로덕션)

- `DEBUG=False` 이고 `DJANGO_USE_HTTPS=1`(기본)일 때: SSL 리다이렉트, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, HSTS 등이 켜집니다.
- 로컬에서 `DEBUG=False` + HTTP 만 쓸 때는 `DJANGO_USE_HTTPS=0` 으로 설정하세요.

## 비밀 정보

- **SECRET_KEY**, **포트원 API 키**는 코드에 넣지 말고 환경변수 또는 `.env`만 사용하세요. (`.env`는 Git에 커밋하지 않음)
- `python-dotenv` 설치 시 프로젝트 루트의 `.env`가 자동 로드됩니다.

## CSRF

- 폼은 `{% csrf_token %}` 유지.
- 별도 도메인/HTTPS에서 CSRF 오류 시 `CSRF_TRUSTED_ORIGINS`에 출처를 추가하세요.

## 기타

- 비밀번호 최소 길이 10자 (`AUTH_PASSWORD_VALIDATORS`).
- 업로드 크기 제한: `DATA_UPLOAD_MAX_MEMORY_SIZE` / `FILE_UPLOAD_MAX_MEMORY_SIZE`.

배포 전 `python manage.py check --deploy` 로 추가 점검을 권장합니다.
