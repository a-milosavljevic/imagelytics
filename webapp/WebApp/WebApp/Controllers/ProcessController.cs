using Microsoft.AspNet.Identity;
using System;
using System.Collections.Generic;
using System.Drawing;
using System.Drawing.Imaging;
using System.IO;
using System.Linq;
using System.Web;
using System.Web.Mvc;
using WebApp.Models;

namespace WebApp.Controllers
{
    [Authorize]
    public class ProcessController : Controller
    {
        public ActionResult Index()
        {
            var userId = User.Identity.GetUserId();

            using (var data = new Entities())
            {
                ViewBag.Projects = data.Projects.Where(x => x.UserId == userId && x.State != 0).OrderByDescending(x => x.Id).ToList();
                return View();
            }
        }

        public ActionResult Project(int projectId = 0)
        {
            var userId = User.Identity.GetUserId();

            ViewBag.PercentComplete = 0;

            using (var data = new Entities())
            {
                var models = data.TrainedModels.Where(x => x.Available).OrderBy(x => x.Position).ToList();
                ViewBag.Models = models;

                if (projectId == 0)
                {
                    var newProject = data.Projects.Where(x => x.UserId == userId && x.State == 0).FirstOrDefault();
                    var defaultModelId = data.TrainedModels.Where(x => x.Available).OrderBy(x => x.Position).Select(x => x.Id).FirstOrDefault();
                    if (newProject == null)
                    {
                        var now = DateTime.UtcNow;

                        newProject = new Projects
                        {
                            State = 0, // 0 - New, 1 - Draft, 2 - Processing, 3 - Completed
                            UserId = userId,
                            ModelId = defaultModelId,
                            DateCreated = now,
                            DateModified = now
                        };

                        data.Projects.Add(newProject);
                        data.SaveChanges();
                    }
                    else
                    {
                        newProject.Title = null;
                        newProject.Description = null;
                        newProject.ModelId = defaultModelId;
                        newProject.DateCreated = DateTime.UtcNow;
                        newProject.DateModified = newProject.DateCreated;
                        data.SaveChanges();
                    }

                    var projectImages = newProject.ProjectImages.ToList();

                    var classStatistics = newProject.ProjectImages.GroupBy(x => x.Class1).Select(x => new ClassStatisticsModel
                    {
                        ClassName = x.Key ?? "",
                        ImageCount = x.Count(),
                        Percentage = Math.Round(100 * x.Count() / ((double)projectImages.Count), 2).ToString("0.00")
                    }).OrderByDescending(x => x.Percentage).ToList();

                    ViewBag.Project = newProject;
                    ViewBag.ProjectImages = projectImages;
                    if (projectImages.Count > 0)
                    {
                        ViewBag.PercentComplete = (int)Math.Round(100 * projectImages.Count(x => x.State != 1) / ((double)projectImages.Count));
                    }
                    ViewBag.ClassStatistics = classStatistics;                    
                }
                else
                {                    
                    var project = data.Projects.Where(x => x.UserId == userId && x.Id == projectId).SingleOrDefault();
                    if (project != null)
                    {
                        var projectImages = project.ProjectImages.Select(x => new ProjectImageModel
                        {
                            Id = x.Id,
                            State = x.State,
                            ProjectId = x.ProjectId,
                            Name = x.Name,
                            Size = x.Size ?? 0,
                            ClassName1 = x.Class1 ?? "",
                            ClassProbability1 = Math.Round(100 * x.ClassProbability1 ?? 0, 2).ToString("0.00"),
                            ClassName2 = x.Class2 ?? "",
                            ClassProbability2 = Math.Round(100 * x.ClassProbability2 ?? 0, 2).ToString("0.00"),
                            ClassName3 = x.Class3 ?? "",
                            ClassProbability3 = Math.Round(100 * x.ClassProbability3 ?? 0, 2).ToString("0.00"),
                            ClassName4 = x.Class4 ?? "",
                            ClassProbability4 = Math.Round(100 * x.ClassProbability4 ?? 0, 2).ToString("0.00"),
                            ClassName5 = x.Class5 ?? "",
                            ClassProbability5 = Math.Round(100 * x.ClassProbability5 ?? 0, 2).ToString("0.00")
                        }).ToList();

                        var classStatistics = project.ProjectImages.GroupBy(x => x.Class1).Select(x => new ClassStatisticsModel
                        {
                            ClassName = x.Key ?? "",
                            ImageCount = x.Count(),
                            Percentage = Math.Round(100 * x.Count() / ((double)projectImages.Count), 2).ToString("0.00")
                        }).OrderByDescending(x => x.Percentage).ToList();
                        
                        ViewBag.Project = project;
                        ViewBag.ProjectImages = projectImages;
                        if (projectImages.Count > 0)
                        {
                            ViewBag.PercentComplete = (int)Math.Round(100 * projectImages.Count(x => x.State != 1) / ((double)projectImages.Count));
                        }
                        ViewBag.ClassStatistics = classStatistics;
                    }
                }                

                return View();
            }
        }

        #region Dropzone

        [HttpPost]
        public ActionResult FileUpload(int projectId)
        {
            bool isSavedSuccessfully = true;
            string msg = "Error saving file!";
            string name = "";
            try
            {
                foreach (string fileName in Request.Files)
                {
                    HttpPostedFileBase file = Request.Files[fileName];

                    // Save file content goes here                    
                    if (file != null && file.ContentLength > 0)
                    {
                        var dot = file.FileName.LastIndexOf('.');
                        name = file.FileName.Substring(0, dot);

                        using (var data = new Entities())
                        {
                            var project = data.Projects.Where(x => x.Id == projectId).SingleOrDefault();
                            if (project != null)
                            {
                                var query = data.ProjectImages.Where(x => x.ProjectId == projectId && string.Compare(x.Name, name, true) == 0);
                                if (query.Count() == 0)
                                {
                                    // Create optimized image and save it as JPG
                                    var img = Image.FromStream(file.InputStream);
                                    if (img.Width > 0 && img.Height > 0)
                                    {
                                        var bmp = CreateOptimizedImage(img);
                                        img.Dispose();

                                        var path = Path.Combine(Server.MapPath("~/img"), string.Format("{0}", projectId));
                                        if (!System.IO.Directory.Exists(path)) System.IO.Directory.CreateDirectory(path);
                                        var fpath = Path.Combine(path, string.Format("{0}.jpg", name));

                                        var encoder = ImageCodecInfo.GetImageEncoders().First(c => c.FormatID == ImageFormat.Jpeg.Guid);
                                        var encParams = new EncoderParameters() { Param = new[] { new EncoderParameter(Encoder.Quality, 80L) } };
                                        bmp.Save(fpath, encoder, encParams);
                                        FileInfo fi = new FileInfo(fpath);

                                        // Snima sliku u bazu
                                        var image = new ProjectImages();
                                        image.State = 0; // New image
                                        image.ProjectId = projectId;
                                        image.Name = name;
                                        image.Size = (int)fi.Length;

                                        data.ProjectImages.Add(image);

                                        if (project.State == 0) project.State = 1; // Change state to Draft for New projects
                                        project.DateModified = DateTime.UtcNow;
                                        data.SaveChanges();
                                    }
                                    else
                                    {
                                        isSavedSuccessfully = false;
                                        msg = "Invalid image file!";
                                    }
                                }
                                else
                                {
                                    isSavedSuccessfully = false;
                                    msg = "Image with the same name is already present in the project!";
                                }
                            }
                            else
                            {
                                isSavedSuccessfully = false;
                                msg = string.Format(@"Cannot find project with ID {0}!", projectId);
                            }
                        }
                    }
                }
            }
            catch (Exception)
            {
                isSavedSuccessfully = false;
            }

            if (isSavedSuccessfully)
            {
                return Json(new { Message = name });
            }
            else
            {
                Response.ClearHeaders();
                Response.ClearContent();
                Response.StatusCode = 500;
                Response.StatusDescription = "Internal Error";
                return Json(new { Message = msg });
            }
        }

        private Bitmap CreateOptimizedImage(Image img)
        {
            int w = img.Width;
            int h = img.Height;
            if (w >= h)
            {
                w = Math.Min(1024, img.Width);
                h = (int)Math.Round(w * img.Height / ((double)img.Width));
            }
            else
            {
                h = Math.Min(1024, img.Height);
                w = (int)Math.Round(h * img.Width / ((double)img.Height));
            }

            return ProcessImage(img, w, h);
        }

        private Bitmap ProcessImage(Image img, int w, int h)
        {
            var bmp = new Bitmap(w, h, PixelFormat.Format24bppRgb);
            using (Graphics g = Graphics.FromImage(bmp))
            {
                g.Clear(Color.White);
                g.InterpolationMode = System.Drawing.Drawing2D.InterpolationMode.Bicubic;
                g.DrawImage(img, 0, 0, bmp.Width, bmp.Height);
            }

            // Fix orientation if needed.
            const int OrientationKey = 0x0112;
            const int NotSpecified = 0;
            const int NormalOrientation = 1;
            const int MirrorHorizontal = 2;
            const int UpsideDown = 3;
            const int MirrorVertical = 4;
            const int MirrorHorizontalAndRotateRight = 5;
            const int RotateLeft = 6;
            const int MirorHorizontalAndRotateLeft = 7;
            const int RotateRight = 8;

            if (img.PropertyIdList.Contains(OrientationKey))
            {
                var orientation = (int)img.GetPropertyItem(OrientationKey).Value[0];
                switch (orientation)
                {
                    case NotSpecified: // Assume it is good.
                    case NormalOrientation:
                        // No rotation required.
                        break;
                    case MirrorHorizontal:
                        bmp.RotateFlip(RotateFlipType.RotateNoneFlipX);
                        break;
                    case UpsideDown:
                        bmp.RotateFlip(RotateFlipType.Rotate180FlipNone);
                        break;
                    case MirrorVertical:
                        bmp.RotateFlip(RotateFlipType.Rotate180FlipX);
                        break;
                    case MirrorHorizontalAndRotateRight:
                        bmp.RotateFlip(RotateFlipType.Rotate90FlipX);
                        break;
                    case RotateLeft:
                        bmp.RotateFlip(RotateFlipType.Rotate90FlipNone);
                        break;
                    case MirorHorizontalAndRotateLeft:
                        bmp.RotateFlip(RotateFlipType.Rotate270FlipX);
                        break;
                    case RotateRight:
                        bmp.RotateFlip(RotateFlipType.Rotate270FlipNone);
                        break;
                    default:
                        //--- throw new NotImplementedException("An orientation of " + orientation + " isn't implemented.");
                        break;
                }
            }

            return bmp;
        }        

        [HttpPost]
        public ActionResult DeleteImage(int projectId, string filename)
        {            
            bool valid = true;
            string msg = "";

            var userId = User.Identity.GetUserId();

            var dot = filename.LastIndexOf('.');
            var name = filename.Substring(0, dot);

            using (var data = new Entities())
            {
                var image = data.ProjectImages.Where(x => x.ProjectId == projectId && string.Compare(x.Name, name) == 0 && x.Projects.UserId == userId).SingleOrDefault();
                if (image != null)
                {
                    string path = Path.Combine(Server.MapPath("~/img"), string.Format("{0}", projectId));
                    string fname = Path.Combine(path, image.Name + ".jpg");
                    string fnameHM = Path.Combine(path, image.Name + "_HM.jpg");                    

                    data.ProjectImages.Remove(image);

                    var project = data.Projects.Where(x => x.Id == projectId).SingleOrDefault();
                    if (project != null)
                    {
                        project.DateModified = DateTime.UtcNow;
                    }
                    data.SaveChanges();

                    // Delete image from the filesystem
                    System.IO.File.Delete(fname);
                    System.IO.File.Delete(fnameHM);
                }
                else
                {
                    valid = false;
                    msg = string.Format("Failed to delete image! Cannot find image \"{0}\" on project ID {1}.", name, projectId);
                }
            }

            return Json(new
            {
                valid = valid,
                message = msg
            });
        }

        #endregion

        [HttpPost]
        public ActionResult SetProjectTitle(int projectId, string val)
        {
            bool valid = true;
            string msg = "";

            var userId = User.Identity.GetUserId();

            using (var data = new Entities())
            {
                var project = data.Projects.Where(x => x.Id == projectId && x.UserId == userId).SingleOrDefault();
                if (project != null)
                {
                    if (project.State == 0 && !string.IsNullOrEmpty(val)) project.State = 1; // Change state to Draft for New projects
                    project.Title = val;
                    project.DateModified = DateTime.UtcNow;
                    data.SaveChanges();
                }
                else
                {
                    valid = false;
                    msg = string.Format("Cannot find project ID {0}!", projectId);
                }
            }

            return Json(new
            {
                valid = valid,
                message = msg
            });
        }

        [HttpPost]
        public ActionResult SetProjectDescription(int projectId, string val)
        {
            bool valid = true;
            string msg = "";

            var userId = User.Identity.GetUserId();

            using (var data = new Entities())
            {
                var project = data.Projects.Where(x => x.Id == projectId && x.UserId == userId).SingleOrDefault();
                if (project != null)
                {
                    if (project.State == 0 && !string.IsNullOrEmpty(val)) project.State = 1; // Change state to Dratf for New projects
                    project.Description = val;
                    project.DateModified = DateTime.UtcNow;
                    data.SaveChanges();
                }
                else
                {
                    valid = false;
                    msg = string.Format("Cannot find project ID {0}!", projectId);
                }
            }

            return Json(new
            {
                valid = valid,
                message = msg
            });
        }

        [HttpPost]
        public ActionResult SetProjectModel(int projectId, string val)
        {
            bool valid = true;
            string msg = "";

            var userId = User.Identity.GetUserId();

            int modelId;
            if (!int.TryParse(val, out modelId)) modelId = 0;            

            using (var data = new Entities())
            {
                var model = data.TrainedModels.Where(x => x.Id == modelId && x.Available).SingleOrDefault();
                if (model != null)
                {
                    var project = data.Projects.Where(x => x.Id == projectId && x.UserId == userId).SingleOrDefault();
                    if (project != null)
                    {
                        project.ModelId = model.Id;
                        project.DateModified = DateTime.UtcNow;
                        data.SaveChanges();
                    }
                    else
                    {
                        valid = false;
                        msg = string.Format("Cannot find project ID {0}!", projectId);
                    }
                }
                else
                {
                    valid = false;
                    msg = string.Format("Cannot find model ID {0}!", val);
                }
            }

            return Json(new
            {
                valid = valid,
                message = msg
            });
        }

        [HttpPost]
        public ActionResult ProcessProject(int projectId)
        {
            bool valid = true;
            string msg = "";

            var userId = User.Identity.GetUserId();

            using (var data = new Entities())
            {
                var project = data.Projects.Where(x => x.Id == projectId && x.UserId == userId).SingleOrDefault();
                if (project != null)
                {
                    if (project.ProjectImages.Count() > 0)
                    {
                        foreach(var image in project.ProjectImages)
                        {
                            image.State = 1; // Ready to process
                        }
                        project.State = 2; // Ready to process                        
                        data.SaveChanges();
                    }
                    else
                    {
                        valid = false;
                        msg = string.Format("Project ID {0} has no images!", projectId);
                    }
                }
                else
                {
                    valid = false;
                    msg = string.Format("Cannot find project ID {0}!", projectId);
                }
            }

            return Json(new
            {
                valid = valid,
                message = msg
            });
        }

        [HttpPost]
        public ActionResult EditProject(int projectId)
        {
            bool valid = true;
            string msg = "";

            var userId = User.Identity.GetUserId();

            using (var data = new Entities())
            {
                var project = data.Projects.Where(x => x.Id == projectId && x.UserId == userId).SingleOrDefault();
                if (project != null)
                {
                    foreach (var image in project.ProjectImages)
                    {
                        image.State = 0; // Unprocessed image
                    }
                    project.State = 1; // Edit project
                    data.SaveChanges();                    
                }
                else
                {
                    valid = false;
                    msg = string.Format("Cannot find project ID {0}!", projectId);
                }
            }

            return Json(new
            {
                valid = valid,
                message = msg
            });
        }

        [HttpPost]
        public ActionResult DeleteProject(int projectId)
        {
            bool valid = true;
            string msg = "";

            var userId = User.Identity.GetUserId();

            using (var data = new Entities())
            {                
                var project = data.Projects.Where(x => x.Id == projectId && x.UserId == userId).SingleOrDefault();
                if (project != null)
                {
                    data.Database.ExecuteSqlCommand(string.Format("DELETE FROM [ProjectImages] WHERE [ProjectId] = {0}", projectId));
                    data.Database.ExecuteSqlCommand(string.Format("DELETE FROM [Projects] WHERE [Id] = {0}", projectId));

                    string path = Path.Combine(Server.MapPath("~/img"), string.Format("{0}", projectId));
                    System.IO.DirectoryInfo dirInfo = new DirectoryInfo(path);
                    if (dirInfo.Exists)
                    {
                        dirInfo.Delete(true);                        
                    }
                }
                else
                {
                    valid = false;
                    msg = string.Format("Cannot find project ID {0}!", projectId);
                }                                
            }

            return Json(new
            {
                valid = valid,
                message = msg
            });
        }

        [HttpPost]
        public ActionResult GetProjectCompletePrecentage(int projectId)
        {
            bool valid = true;
            string msg = "";
            int percentComplete = 0;
            byte state = 255;

            var userId = User.Identity.GetUserId();

            using (var data = new Entities())
            {
                var project = data.Projects.Where(x => x.Id == projectId && x.UserId == userId).SingleOrDefault();
                if (project != null)
                {
                    int cnt = project.ProjectImages.Count();
                    if(cnt > 0)
                    {                     
                        percentComplete = (int)Math.Round(100 * project.ProjectImages.Count(x => x.State != 1) / ((double)cnt));
                    }
                    state = project.State;
                }
                else
                {
                    valid = false;
                    msg = string.Format("Cannot find project ID {0}!", projectId);
                }
            }

            return Json(new
            {
                valid = valid,
                msg = msg,
                percentComplete = percentComplete,
                state = state
            });
        }
    }
}
