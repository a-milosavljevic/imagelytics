using System.ComponentModel.DataAnnotations;
using System.Data.Entity;
using System.Security.Claims;
using System.Threading.Tasks;
using Microsoft.AspNet.Identity;
using Microsoft.AspNet.Identity.EntityFramework;

namespace WebApp.Models
{
    // You can add profile data for the user by adding more properties to your ApplicationUser class, please visit https://go.microsoft.com/fwlink/?LinkID=317594 to learn more.
    public class ApplicationUser : IdentityUser
    {
        // Package Manager Console
        // -----------------------
        // Step 1 (only once for the project): Enable-Migrations -EnableAutomaticMigrations
        // Step 2 (update on code change):     Update-Database -Force                

        [MaxLength(64)]
        public string FirstName { get; set; }
        
        [MaxLength(128)]
        public string LastName { get; set; }
        
        [MaxLength(256)]
        public string Institution { get; set; }

        [MaxLength(128)]
        public string Domain { get; set; }

        [MaxLength(100)]
        public string IntendedUse { get; set; }

        public int Credits { get; set; }

        public async Task<ClaimsIdentity> GenerateUserIdentityAsync(UserManager<ApplicationUser> manager)
        {
            // Note the authenticationType must match the one defined in CookieAuthenticationOptions.AuthenticationType
            var userIdentity = await manager.CreateIdentityAsync(this, DefaultAuthenticationTypes.ApplicationCookie);
            // Add custom user claims here
            return userIdentity;
        }
    }

    public class ApplicationDbContext : IdentityDbContext<ApplicationUser>
    {
        public ApplicationDbContext()
            : base("DefaultConnection", throwIfV1Schema: false)
        {
        }

        public static ApplicationDbContext Create()
        {
            return new ApplicationDbContext();
        }
    }
}