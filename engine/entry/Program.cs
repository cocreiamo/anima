// The HTTP entry point's host program (ADR 0008, GAP-058). It holds no route and
// no TLS setting: the routes are the `ReverseProxy` section of appsettings.json
// and the listeners and certificates are `Kestrel` settings of the unit.
//
// The one thing it decides itself is what is never forwarded (R129): a request
// whose path has a segment that names a health, metrics or management endpoint
// of a backend is answered 404 before any route is looked at, whatever the
// configuration declares.

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddReverseProxy().LoadFromConfig(builder.Configuration.GetSection("ReverseProxy"));
var app = builder.Build();

string[] neverForwarded = ["health", "metrics", "management", "q"];

app.Use(async (context, next) =>
{
    var segments = context.Request.Path.Value?.Split('/', StringSplitOptions.RemoveEmptyEntries) ?? [];
    if (segments.Any(s => neverForwarded.Contains(s, StringComparer.OrdinalIgnoreCase)))
    {
        context.Response.StatusCode = StatusCodes.Status404NotFound;
        return;
    }
    await next();
});

app.MapReverseProxy();
app.Run();
