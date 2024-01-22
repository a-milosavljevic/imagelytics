using System.Web;
using System.Web.Optimization;

namespace WebApp
{
    public class BundleConfig
    {
        // For more information on bundling, visit https://go.microsoft.com/fwlink/?LinkId=301862
        public static void RegisterBundles(BundleCollection bundles)
        {
            bundles.Add(new ScriptBundle("~/bundles/jquery").Include(
                        "~/Scripts/jquery-{version}.js"));

            bundles.Add(new ScriptBundle("~/bundles/jqueryval").Include(
                        "~/Scripts/jquery.validate*"));

            // Use the development version of Modernizr to develop with and learn from. Then, when you're
            // ready for production, use the build tool at https://modernizr.com to pick only the tests you need.
            bundles.Add(new ScriptBundle("~/bundles/modernizr").Include(
                        "~/Scripts/modernizr-*"));

            bundles.Add(new ScriptBundle("~/bundles/bootstrap").Include(
                      "~/Scripts/bootstrap.js",
                      "~/Scripts/bootbox.js",
                      "~/Scripts/imagelytics.js"));

            bundles.Add(new StyleBundle("~/Content/css").Include(
                      "~/Content/bootstrap.css",
                      "~/Content/font-awesome.css",
                      "~/Content/site.css"));

            // Dropzone.js
            bundles.Add(new ScriptBundle("~/bundles/dropzone").Include(
                        "~/Scripts/dropzone/dropzone.js"));
            bundles.Add(new StyleBundle("~/Content/dropzone").Include(
                        "~/Scripts/dropzone/basic.css",
                        "~/Scripts/dropzone/dropzone.css"));

            // Datatables
            bundles.Add(new ScriptBundle("~/bundles/data-tables").Include(
                        "~/Scripts/DataTables/jquery.dataTables.js",
                        "~/Scripts/DataTables/dataTables.bootstrap.js",
                        "~/Scripts/DataTables/dataTables.responsive.js",
                        "~/Scripts/DataTables/responsive.bootstrap.js",
                        "~/Scripts/DataTables/dataTables.select.js"));
            bundles.Add(new StyleBundle("~/Content/data-tables").Include(
                        "~/Content/DataTables/css/dataTables.bootstrap.css", new CssRewriteUrlTransform()).Include(
                        "~/Content/DataTables/css/responsive.bootstrap.css", new CssRewriteUrlTransform()).Include(
                        "~/Content/DataTables/css/select.dataTables.css", new CssRewriteUrlTransform()));
        }
    }
}
