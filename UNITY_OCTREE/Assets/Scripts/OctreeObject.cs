using UnityEngine;

namespace Octrees
{
    public class OctreeObject
    {
        public Bounds bounds;
        public GameObject obj;
        
        public OctreeObject(GameObject obj)
        {
            this.obj = obj;
            bounds = obj.GetComponent<Collider>().bounds;
        }
        
        public bool Intersects(Bounds boundsToCheck) => bounds.Intersects(boundsToCheck);
        
        
    }
}