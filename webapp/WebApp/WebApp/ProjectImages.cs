//------------------------------------------------------------------------------
// <auto-generated>
//     This code was generated from a template.
//
//     Manual changes to this file may cause unexpected behavior in your application.
//     Manual changes to this file will be overwritten if the code is regenerated.
// </auto-generated>
//------------------------------------------------------------------------------

namespace WebApp
{
    using System;
    using System.Collections.Generic;
    
    public partial class ProjectImages
    {
        public int Id { get; set; }
        public byte State { get; set; }
        public int ProjectId { get; set; }
        public string Name { get; set; }
        public Nullable<int> Size { get; set; }
        public string Class1 { get; set; }
        public Nullable<float> ClassProbability1 { get; set; }
        public string Class2 { get; set; }
        public Nullable<float> ClassProbability2 { get; set; }
        public string Class3 { get; set; }
        public Nullable<float> ClassProbability3 { get; set; }
        public string Class4 { get; set; }
        public Nullable<float> ClassProbability4 { get; set; }
        public string Class5 { get; set; }
        public Nullable<float> ClassProbability5 { get; set; }
    
        public virtual Projects Projects { get; set; }
    }
}
