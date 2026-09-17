import { AlbumSearch } from "@/components/album-search";
import { api, type Health } from "@/lib/api";

async function getHealth(): Promise<Health | null> {
  try {
    return await api.health();
  } catch {
    return null;
  }
}

export default async function HomePage() {
  const health = await getHealth();

  return (
    <div className="space-y-10">
      <section className="space-y-3">
        <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">
          Track the albums you listen to.
        </h1>
        <p className="max-w-xl text-muted">
          Rate them, write about them, and see what your friends are spinning. Start by finding
          something you have on repeat.
        </p>
      </section>

      <AlbumSearch />

      <p className="text-xs text-muted">
        API:{" "}
        {health ? (
          <span className="text-foreground">
            v{health.version} · database {health.database}
          </span>
        ) : (
          <span className="text-danger">unreachable (is the backend running on :8001?)</span>
        )}
      </p>
    </div>
  );
}
